import { getRandom, getRegex, getRegexWithAlphabit } from "./supabase.js"
import { initPy } from "./loadpy.js"

const pyodide = await initPy()
const supabase4js = {
    getRandom: getRandom,
    getRegex: getRegex,
    getRegexWithAlphabit: getRegexWithAlphabit,
}
pyodide.registerJsModule("supabase4js", supabase4js);
console.log("Registered supabase4js");
console.log(await pyodide.runPythonAsync(`
    from platyrhynchos.cruciverbalists.en_simple import get_random
    get_random()
    `)
);