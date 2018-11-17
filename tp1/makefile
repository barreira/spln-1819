all: chemical chemicalLatex chemicalPlot latexToPdf

chemical:
	pyinstaller --onefile chemical.py
	sudo cp dist/chemical /usr/local/bin
	rm -rf dist build __pycache__ chemical.spec

chemicalLatex:
	pyinstaller --onefile chemicalLatex.py
	sudo cp dist/chemicalLatex /usr/local/bin
	sudo mkdir -p /usr/local/bin/resources
	sudo cp -R resources/Front.jpg resources/periodic_table.info /usr/local/bin/resources
	rm -rf dist build __pycache__ chemicalLatex.spec

chemicalPlot:
	pyinstaller --onefile chemicalPlot.py
	sudo cp dist/chemicalPlot /usr/local/bin
	rm -rf dist build __pycache__ chemicalPlot.spec

latexToPdf:
	sudo cp latexToPdf.sh /usr/local/bin/latexToPdf
	sudo chmod +x /usr/local/bin/latexToPdf

clean:
	sudo rm -rf /usr/local/bin/chemical /usr/local/bin/chemicalLatex /usr/local/bin/printChemLatex.py /usr/local/bin/chemicalPlot /usr/local/bin/latexToPdf /usr/local/bin/resources
