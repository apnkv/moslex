<%inherit file="app.mako"/>

<%block name="head">
    <link href="${request.static_url('moslex:static/project.css')}" rel="stylesheet">
</%block>

## <%block name="header">
##     <a href="${request.route_url('dataset')}">
##         <img src="${request.static_url('moslex:static/header.gif')}"/>
##     </a>
## </%block>

<%block name="navextra">
    <div class="nav pull-right">
        <ul class="nav navbar-nav ">
            <li id="menuitem_report">
                <div id="comment-button-paragraph">
                    <a href="mailto:alexei.kassian@gmail.com?subject=MosLex: ${request.url}"
                       title="Comment or report error"
                       class="btn btn-default navbar-btn"
                    >Comment or report an error</a>
                </div>
            </li>
        </ul>
    </div>
</%block>

${next.body()}
