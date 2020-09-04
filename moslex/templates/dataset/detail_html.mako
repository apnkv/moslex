<%inherit file="../home_comp.mako"/>

<%! from datetime import datetime%>

<%def name="sidebar()">
##     <div class="well">
##         <h3>Sidebar</h3>
##         <p>
##             Content
##         </p>
##     </div>
</%def>

## <div>
<h1>Moscow Lexical Database</h1>

<p>Welcome to MosLex.</p>
<p>Moscow Lexical Database (MosLex) is a collection of basic vocabularies of languages all around the world. MosLex comprises annotated basic wordlists of living, recently extinct, and ancient languages, as well as those of reconstructed proto-languages. A wordlist appears in MosLex if it meets the following key conditions: it is of high lexicographic quality, it is detailed in linguistic and philological elaboration, and complies with our semantic standards and our overall methodology.</p>
<h2>How to cite</h2>
<p>Kassian, Alexei S. (ed.). 2020. Moscow lexical database. <a href="https://pnkv.ru/">https://pnkv.ru/</a> (accessed: ${datetime.now().strftime("%d %b %Y")}) </p>
## </div>
