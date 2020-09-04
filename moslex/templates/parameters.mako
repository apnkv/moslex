<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%! active_menu_item = "parameters" %>

<h3>Concepts</h3>
${dt.render()}
