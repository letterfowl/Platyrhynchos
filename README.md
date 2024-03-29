<br/>
<p align="center">
  <h1 align="center">🦆 Platyrhynchos 🦆</h1>

  <p align="center">
    Automatic crossword generator!
    <br/>
    <a href="https://hfhr.pl/en/news,964166344:323067518" title="Learn about Poland's constitutional crisis and support the fight!">🏳️‍🌈🇵🇱🇪🇺</a>
    <br/>
    <br/>
    <a href="https://github.com/letterfowl/Platyrhynchos/wiki"><strong>Explore the docs »</strong></a>
    <br/>
    <br/>
  </p>
</p>

![Repo size](https://img.shields.io/github/repo-size/letterfowl/Platyrhynchos)
[![OSSAR](https://github.com/letterfowl/Platyrhynchos/actions/workflows/ossar.yml/badge.svg)](https://github.com/letterfowl/Platyrhynchos/actions/workflows/ossar.yml)
[![CodeQL](https://github.com/letterfowl/Platyrhynchos/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/letterfowl/Platyrhynchos/actions/workflows/github-code-scanning/codeql)
[![GuardRails badge](https://api.guardrails.io/v2/badges/185469?token=1ea3826f490818d69186624aaa9d02cdf330f4447d1ad90f54120574dd0ce04b)](https://dashboard.guardrails.io/gh/letterfowl/repos/185469)
[![autoflake, isort, black](https://github.com/letterfowl/Platyrhynchos/actions/workflows/format.yml/badge.svg)](https://github.com/letterfowl/Platyrhynchos/actions/workflows/format.yml)
[![.github/workflows/pytest.yml](https://github.com/letterfowl/Platyrhynchos/actions/workflows/pytest.yml/badge.svg)](https://github.com/letterfowl/Platyrhynchos/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/letterfowl/Platyrhynchos/branch/main/graph/badge.svg?token=5HNARDOWC6)](https://codecov.io/gh/letterfowl/Platyrhynchos)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Table Of Contents

- [Table Of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [0.9 release approaches](#09-release-approaches)
  - [Our new approach](#our-new-approach)
- [Built With](#built-with)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
  - [Creating A Pull Request](#creating-a-pull-request)
- [License](#license)
- [Contributors](#contributors)
- [Acknowledgments](#acknowledgements)

## About The Project

Platyrhynchos is a project centered around creating word-centric crossword generation algorithms. This can be viewed as an alternative to methods that focus on generating matrices filled with letters and mutating them to make them into crosswords.

Currently, we are investigating a "smart" word insertion method that finds the worst rows and columns and tries to improve their score. Currently, we have implemented a direct search algorithm that works by finding the best word to insert into the row/column and then inserting it. This is repeated until the score of the crossword cannot be improved.

## Built With

- Python
- Poetry
- Pyodide
- PyTest
- functiontrace
- Webpack
- Supabase

## Getting Started

### Pyodide-based execution

1. Move to `app` directory
2. At the same time, run `npm run serve` and `npm run pywatch`. This will start a webpack server and a Pyodide build watcher.
3. Open `localhost:8080` in your browser (although, it should open itself).

### Running the code locally

1. Make sure to have Python 3.10 and Poetry installed
2. Run any of the scripts using `poetry run ...`

## Roadmap

See the [open issues](https://github.com/letterfowl/Platyrhynchos/issues) for a list of proposed features (and known issues). We also use the GitHub Projects tab to track the progress of the project.

## Contributing

Any contributions you make are **greatly appreciated**, but please make sure to get in contact with the authors:
* If you have suggestions for adding or removing projects, feel free to [open an issue](https://github.com/letterfowl/Platyrhynchos/issues/new) to discuss it, or directly create a pull request after you edit the *README.md* file with necessary changes.
* Please make sure you check your spelling and grammar.
* Create individual PR for each suggestion.
* Please also read through the [Code Of Conduct](https://github.com/letterfowl/Platyrhynchos/blob/main/CODE-OF-CONDUCT.md) before posting your first idea as well.

### Creating A Pull Request

1. Clone the project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Add tests and make sure they work!
5. Describe them on our wiki (you can also add doctests there :D)
6. Push to the Branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request, add reviewers

## License

Distributed under the CC Attribution NonCommercial ShareAlike 4.0 International License. See [LICENSE](https://github.com/letterfowl/Platyrhynchos/blob/main/LICENSE) for more information.

## Contributors

<a href = "https://github.com/letterfowl/Platyrhynchos/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=letterfowl/Platyrhynchos"/>
</a>

## Acknowledgements

* [ShaanCoding](https://github.com/ShaanCoding/) - *Built ReadME Template*
* [ImgShields](https://shields.io/)
* [Exolve](https://github.com/viresh-ratnakar/exolve)
* [Cryptic Crossword Clues dataset](https://cryptics.georgeho.org/)
