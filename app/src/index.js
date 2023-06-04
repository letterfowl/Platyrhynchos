import { getRandom, getRegex, getRegexWithAlphabit } from "./supabase.js"
import { initPy } from "./loadpy.js"

const pyodide = await initPy()
const supabase4js = {
    getRandom: getRandom,
    getRegex: getRegex,
    getRegexWithAlphabit: getRegexWithAlphabit,
}
const settings = await (await fetch("settings.toml")).text()
const _stuff = {
    settings_text: settings,
}

pyodide.registerJsModule("supabase4js", supabase4js);
console.log("Registered supabase4js");
pyodide.registerJsModule("_stuff", _stuff);

console.log(await pyodide.runPythonAsync(`
    from platyrhynchos.director.direct_search import generate_crossword

    crossword = generate_crossword(10, 10, 16)
    print(crossword)
    print()
    print("Word amount:", len(crossword.words))
    print("Words:", ",".join(crossword.words.keys()))
    `)
);
