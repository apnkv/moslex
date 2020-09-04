<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

% if ctx.description:
<p>${h.text2html(h.Markup(ctx.markup_description) if ctx.markup_description else ctx.description)}</p>
% endif

% if ctx.confidence:
<dl>
    <dt>${_('Confidence')}:</dt>
    <dd>${ctx.confidence}</dd>
</dl>
% endif

% if ctx.sentence_assocs:
${util.sentences(ctx, fmt='short')}
% endif

% if not ctx.sentence_assocs and not ctx.description and not ctx.confidence:
<p>No details available</p>
% endif
