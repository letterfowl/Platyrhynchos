import * as duckdb from '@duckdb/duckdb-wasm';

async function initDatabase({
  log = false
} = {}) {
  const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();

  // Select a bundle based on browser checks
  const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

  const worker_url = URL.createObjectURL(
    new Blob([`importScripts("${bundle.mainWorker}");`], { type: 'text/javascript' })
  );

  // Instantiate the asynchronus version of DuckDB-wasm
  const worker = new Worker(worker_url);
  const logger = log ? new duckdb.ConsoleLogger() : new duckdb.VoidLogger();
  const db = new duckdb.AsyncDuckDB(logger, worker);
  await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
  URL.revokeObjectURL(worker_url);

  return db;
}

async function runSQL(db, sql) {
  const conn = await db.connect();

  // Query
  const arrowResult = await conn.query(sql);

  // Convert arrow table to json
  const result = arrowResult.toArray().map((row) => row.toJSON());

  // Close the connection to release memory
  await conn.close();

  return result;
}

export async function set_up_database() {
  const db = await initDatabase({ log: true });
  const res = await fetch("s3/en_simple.parquet");
  console.info("Got parquet file")
  await db.registerFileBuffer('buffer.parquet', new Uint8Array(await res.arrayBuffer()));
  console.info("Registered parquet file")
  const connection = await db.connect();
  await connection.query("CREATE TABLE en_simple AS SELECT * FROM 'buffer.parquet'");
  await connection.query("ALTER TABLE en_simple ALTER alphabit_raw TYPE BITSTRING");
  await connection.query("ALTER TABLE en_simple RENAME alphabit_raw TO alphabit");
  await connection.close();
  console.info("Alphabit column converted")
  if ((await runSQL(db, "SELECT alphabit FROM en_simple LIMIT 10")).length > 0) {
    console.info("Database set up and tested successfully!")
  }
  else {
    console.error("Database set up failed!")
  }
  return db;
}

export async function prepare_functions() {
  const db = await set_up_database();

  return {
    db: db,

    get_regex_w_alphabit: async function(regex, alphabit, previous, limit = 20) {
      previous = previous.map(i => `'${i}'`);
      if (previous.length == 0) {
        previous = ["'A'"];
      }
      const sql = `select distinct answer from en_simple where bit_count('${alphabit}'::BIT | alphabit)=length(alphabit) and regexp_matches(answer, '${regex}') and length(answer) > 1 and length(answer) > 1 and answer not in (${previous.join(',')}) order by random() limit ${limit}`;
      return await runSQL(db, sql).then(db => db.map(i => i.answer));
    },
    
    get_regex: async function(regex, previous, limit = 20) {
      previous = previous.map(i => `'${i}'`);
      if (previous.length == 0) {
        previous = ["'A'"];
      }
      const sql = `select distinct answer from en_simple where regexp_matches(answer, '${regex}') and length(answer) > 1 and answer not in (${previous.join(',')}) order by random() limit ${limit}`;
      return await runSQL(db, sql).then(db => db.map(i => i.answer));
    },
    
    get_random: async function(max_size) {
      const sql = `select distinct answer from en_simple where length(answer) > 1 and length(answer) < ${max_size} order by random() limit 1`;
      return await runSQL(db, sql).then(db => db.map(i => i.answer));
    }
  }
}
