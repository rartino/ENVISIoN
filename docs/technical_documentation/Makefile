all: technical_documentation.pdf lips_technical_documentation.pdf

technical_documentation.pdf: technical_documentation.tex
	NAME=$$(basename "$<" .tex); \
	latexmk -pdf "$$NAME".tex

technical_documentation.tex: technical_documentation.rst
	NAME=$$(basename "$<" .rst); \
	rst2latex --no-section-numbering --use-latex-toc --use-latex-citations "$<" | \
		sed 's/\\hyperref\[\([^]]\+\)\]{[^}]\+}/\\ref{\1}/g' | \
		sed 's/\\phantomsection//g' | \
		perl -pe 'BEGIN{undef $$/;} s/\\section\{[^a-zA-Z]*Referenser[^}]*\\label\{referenser\}[^}]*\}//smg' | \
		perl -pe 'BEGIN{undef $$/;} s/(\\label\{[^}]*\})\s*\\caption\{(.*?)\}\s*\\end\{figure\}/\n\\caption{\2\1}\n\\end{figure}/smg' > "$$NAME".tex; 

lips_technical_documentation.pdf: technical_documentation.pdf lips_technical_documentation.tex technical_documentation_stripped.tex Lips/Appendix_old_tekniskdok.tex  Lips/LicensAppendixtext.tex  Lips/LIPS.tex Lips/DokumentHistorik.tex Lips/Lips-front.tex
	latexmk -pdf lips_technical_documentation.tex

technical_documentation_stripped.tex: technical_documentation.tex
	awk '/\\section{Bakgrund/{flag=1} /\\end{document}/{flag=0}flag' technical_documentation.tex > technical_documentation_stripped.tex

clean:
	rm -f *~
	rm technical_documentation_stripped.tex
	latexmk -c
