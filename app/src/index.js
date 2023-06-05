import { getRandom, getRegex, getRegexWithAlphabit } from "./supabase.js"
import { initPy } from "./loadpy.js"

const pyodide = await initPy()
const supabase4js = {
    getRandom: getRandom,
    getRegex: getRegex,
    getRegexWithAlphabit: getRegexWithAlphabit,
}
const test_connection = getRegexWithAlphabit(".+", "11111111111111111111111111", "").then((x) => console.info("Connection to Supabase successful!"))

const settings = await (await fetch("settings.toml")).text()
const _stuff = {
    settings_text: settings,
}

pyodide.registerJsModule("supabase4js", supabase4js);
console.log("Registered supabase4js");
pyodide.registerJsModule("_stuff", _stuff);

await test_connection;
console.log(await pyodide.runPythonAsync(`
    from platyrhynchos.director.direct_search import generate_crossword
    from platyrhynchos.cruciverbalist.en_simple import get_regex_w_alphabit

    if await get_regex_w_alphabit(".+", "11111111111111111111111111", []):
        print("Connection to DB via Pyodide successful!")

    crossword = await generate_crossword(10, 10, 16)
    print(crossword)
    print()
    print("Word amount:", len(crossword.words))
    print("Words:", ",".join(crossword.words.keys()))
    `)
);
