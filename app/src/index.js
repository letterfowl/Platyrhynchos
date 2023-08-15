import { getRandom, getRegex, getRegexWithAlphabit } from "./supabase.js"
import { initPy } from "./loadpy.js"
import "./spinner.css"

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
const crossword = await pyodide.runPythonAsync(`
    from platyrhynchos.director.direct_search import generate_crossword
    from platyrhynchos.exclusive import get_regex_w_alphabit

    if await get_regex_w_alphabit(".+", "11111111111111111111111111", []):
        print("Connection to DB via Pyodide successful!")

    crossword = await generate_crossword(10, 10, 10)
    print(crossword)
    print()
    print("Word amount:", len(crossword.words))
    print("Words:", ",".join(crossword.words.keys()))
    crossword.as_exolve()
`);
document.getElementById("spinner").remove();
// const crossword = `
// exolve-begin
//   exolve-id: exolve-example
//   exolve-title: Exolve Example

//   # Uncomment and edit the next two lines if you want to show the setter's name
//   # and/or show a copyright notice.
//   exolve-setter: letterfowl
//   exolve-copyright: 2023 All rights reserved.

//   exolve-width: 10
//   exolve-height: 10
//   exolve-option: allow-chars:-/

//   exolve-grid:
//     PRECIPICEM
//     .H..N.DHMI
//     .Y..C.OION
//     .T..U.LNTN
//     .H..R.IAIE
//     .M..I.SWCS
//     .S..O.EAOO
//     ....U.SRNT
//     DELIS..E.A
//     CHEATED/!ON

//   exolve-option: ignore-unclued
//   # Note that you can provide an annotation after the closing parenthesis in
//   # any clue, which will get shown after the solver "Reveal"s the clue.

//   # The Exolve format has lots of additional features. See details in the
//   # documentation at:
//   #   https://github.com/viresh-ratnakar/exolve/blob/master/README.md
// exolve-end
// `
createExolve(crossword);