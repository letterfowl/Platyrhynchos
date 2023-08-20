import { prepare_functions } from "./duck.js"
import { initPy } from "./loadpy.js"
import "./spinner.css"

function open_plaintext(text) {
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
}

const promise_duckdb_client = prepare_functions();
const pyodide = await initPy()
const duckdb_client = await promise_duckdb_client;
const test_connection = duckdb_client.get_regex_w_alphabit(".+", "11111111111111111111111111", "").then((x) => console.info("Connection to DuckDB successful!"))

const settings = await (await fetch("settings.toml")).text()
const _stuff = {
    settings_text: settings,
}

pyodide.registerJsModule("_duckdb", duckdb_client);
console.log("Registered DuckDB WASM client in Pyodide");
pyodide.registerJsModule("_stuff", _stuff);

await test_connection;
const crossword = await pyodide.runPythonAsync(`
    from platyrhynchos.scripts import simulated_annealing_routine
    from platyrhynchos.exclusive import get_regex_w_alphabit

    if await get_regex_w_alphabit(".+", "11111111111111111111111111", ""):
        print("Connection to DB via Pyodide successful!")

    await simulated_annealing_routine()
`);
document.getElementById("spinner").remove();

open_plaintext(crossword);
