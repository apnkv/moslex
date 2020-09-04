<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

%if ctx.level.value == "language":
    <h2>${_('Language')} ${ctx.name}</h2>
%elif ctx.level.value == "group":
    <h2>Group ${ctx.name}</h2>
%elif ctx.level.value == "family":
    <h2>Family ${ctx.name}</h2>
%else:
    <h2>Languoid ${ctx.name}</h2>
%endif

%if ctx.level.value == "language":
    ${request.get_datatable('values', h.models.Value, language=ctx).render()}
%elif ctx.level.value == "group":
    ${request.get_datatable('values', h.models.Value, language=ctx).render()}
##     <%include file="${ctx.description_file_url}"/>
##
##     Meanwhile, you can download a <a href="${ctx.nex_url}">.nex file for phylogenetic
##     analysis</a>.
%else:
    Only language and group detailed pages are supported right now. TODO: add a list of children.
%endif


<%def name="language_meta(lang=None)">
    <% lang = lang or ctx %>
    <div class="accordion" id="sidebar-accordion">
        % if getattr(request, 'map', False):
            <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
                ${request.map.render()}
                ${h.format_coordinates(lang)}
            </%util:accordion_group>
        % endif
        % if lang.sources:
            <%util:accordion_group eid="sources" parent="sidebar-accordion" title="Sources">
                <ul>
                    % for source in lang.sources:
                        <li>${h.link(request, source, label=source.description)}<br/>
                            <small>${h.link(request, source)}</small></li>
                    % endfor
                </ul>
            </%util:accordion_group>
        % endif
        % if lang.identifiers:
            <%util:accordion_group eid="acc-names" parent="sidebar-accordion" title="${_('Alternative names')}" open="${True}">
                <dl>
                    % for type_, identifiers in h.groupby(sorted(lang.identifiers, key=lambda i: i.type), lambda j: j.type):
                        <dt>${type_}:</dt>
                    % for identifier in identifiers:
                        <dd>${h.language_identifier(request, identifier)}</dd>
                    % endfor
                    % endfor
                </dl>
            </%util:accordion_group>
        % endif
        <%util:accordion_group eid="downloads" parent="sidebar-accordion" title="Downloads" open="${True}">
            <ul>
                %if lang.nex_url:
                    <li><a href="${lang.nex_url}">.nex file</a></li>
                %elif lang.parent.nex_url:
                    <li><a href="${lang.parent.nex_url}">.nex file</a></li>
                %endif
                %if lang.description_file_url:
                    <li><a href="${lang.description_file_url}">Group dataset description</a></li>
                %elif lang.parent.description_file_url:
                    <li><a href="${lang.parent.description_file_url}">Group dataset description</a></li>
                %endif
            </ul>
        </%util:accordion_group>
    </div>
</%def>

<%def name="sidebar()">
    ${language_meta()}
</%def>
