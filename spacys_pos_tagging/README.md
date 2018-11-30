# spaCy's PoS tagging

Web app and terminal client to use spaCy's features

Either launches the web app (if no parameters are provided) or takes an input file and produces output to file or the terminal. This output can be: a table with information about tokens, a bar chart with POS tag frequence, a text tagged with entities or a dependency graph.

Multi-language (Portuguese and English) support via the -l/--lang parameter.

## Installing

Generate tar.gz file

```
python3 setup.py sdist bdist_wheel
```

Install module with tar.gz file

```
pip3 install --user ./dist/spacy_pos_tagging-0.0.1.tar.gz
```

```
python -m spacy download pt
python -m spacy download en_core_web_lg
```

## Built With

* [spaCy](http://http://spacy.io/) - NLP library
* [Flask](http://flask.pocoo.org/) - Web framework
* [matplotlib](https://matplotlib.org/) - Plotting library 

## Authors

* **João Barreira** - [barreira](https://github.com/PurpleBooth)
* **Mafalda Nunes** - [a77364](https://github.com/a77364)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Both our professors at University of Minho for the idea for the project
