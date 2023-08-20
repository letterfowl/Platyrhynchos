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

async function runSQL(db: duckdb.AsyncDuckDB, sql: string) {
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
const db_promise = set_up_database();

export async function database_functions() {
  const db = await db_promise;

  return {
    db: db,

    get_regex_w_alphabit: async function(regex: string, alphabit: string, previous: string, limit = 20) {
      const formatted_previous = previous.split(',').map(i => `'${i}'`).join(',');
      let not_in_statement;
      if (formatted_previous.length == 0) {
        not_in_statement = "";
      }
      else {
        not_in_statement = `and answer not in (${formatted_previous})`;
      }
      const sql = `select distinct answer from en_simple where bit_count('${alphabit}'::BIT | alphabit)=length(alphabit) and regexp_matches(answer, '${regex}') and length(answer) > 1 and length(answer) > 1 ${not_in_statement} order by random() limit ${limit}`;
      return await runSQL(db, sql).then(db => db.map(i => i.answer));
    },
    
    get_regex: async function(regex: string, previous: string, limit = 20) {
      const formatted_previous = previous.split(',').map(i => `'${i}'`).join(',');
      let not_in_statement;
      if (formatted_previous.length == 0) {
        not_in_statement = "";
      }
      else {
        not_in_statement = `and answer not in (${formatted_previous})`;
      }
      const sql = `select distinct answer from en_simple where regexp_matches(answer, '${regex}') and length(answer) > 1 ${not_in_statement} order by random() limit ${limit}`;
      return await runSQL(db, sql).then(db => db.map(i => i.answer));
    },
    
    get_random: async function(max_size: number) {
      const sql = `select distinct answer from en_simple where length(answer) > 1 and length(answer) < ${max_size} order by random() limit 1`;
      return await runSQL(db, sql).then(db => db.map(i => i.answer));
    },

    find_clues: async function(words: string) {
      const sql = `select answer, any_value(clue) as clue from en_simple where answer in (${words}) group by answer`;
      return await runSQL(db, sql).then(db => db.map(i => [i.answer, i.clue]));
    }
  }
}
