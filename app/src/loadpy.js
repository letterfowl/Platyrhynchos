const loadPyodide = require('pyodide')

export async function initPy(){
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    pyodide.loadPackage("setuptools");
    await micropip.install('http://localhost:8080/platyrhynchos-0.1.1-py3-none-any.whl');
    console.log("Loaded pyodide");
    return pyodide;
}
