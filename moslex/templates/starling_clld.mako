<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="navextra">
    <div class="nav pull-right">
        <ul class="nav navbar-nav ">
            <li id="menuitem_report">
                <p style="padding-top: 4px">
                    <a href="mailto:alexei.kassian@gmail.com?subject=MosLex: ${request.url}"
                       title="Comment or report error"
                       class="btn btn-default navbar-btn"
                    >Comment or report an error</a>
                </p>
            </li>
        </ul>
    </div>
</%block>

## <style>
##     .nav a {
##         padding-top: 4px;
##     }
## </style>

${next.body()}
