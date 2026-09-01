# Reducing Cognitive Load

A learner deciding which of eleven menus might contain "insert a picture" is
spending attention on the interface instead of on writing. Every extra
visible-but-irrelevant menu, toolbar, or sidebar panel is something a
beginner has to at least glance at and dismiss before finding what they
actually need. LOUIM's job is to remove that overhead for a given lesson,
without removing the feature permanently.

## The three surfaces that matter most

In practice, three things drive most of the visual noise a beginner
encounters, and LOUIM's menu commands (see the [teacher
guide](../teacher-guide.md)) target exactly these. Menus with nothing
relevant to today's lesson are common candidates to hide early. Tools and
Format ▸ Styles are frequent examples. Configure Menus removes them from the
bar entirely rather than just leaving an empty menu behind, which is all
Tools ▸ Customize can do on its own. Toolbar buttons for features not yet
introduced can go too: setting `"hide_toolbar_buttons_with_menus": true` in
a template means hiding a menu also hides the matching toolbar icons
automatically, so a beginner never sees an Insert Table icon sitting in the
toolbar for a feature whose whole menu is gone. Sidebar panels that aren't
part of the current lesson can be dropped from a template's `sidebar`
section too, such as the Gallery or Styles deck, so the sidebar itself has
fewer competing panels.

## Load reduction is not feature removal

The distinction matters pedagogically as much as technically. Every apply is
non-cumulative and every hide gets recorded so Restore Full Menus can undo it
exactly (see [ui-element-model.md](../ui-element-model.md)). A template that
hides Tools this week isn't a permanent decision. It's a statement about this
lesson, revisable the moment the lesson moves on. That's why LOUIM's starter
templates come in a level-1, level-2, full progression instead of a single
fixed "simplified Writer." Load should decrease early and get added back
deliberately, not stay minimal forever. See
[designing-progressive-writer-courses.md](designing-progressive-writer-courses.md).

## A caution: don't over-hide

Removing too much creates a different kind of friction. A learner who needs
Insert ▸ Table but finds no Insert menu has to ask instead of exploring. The
bundled level-1 templates are a starting point, not a rule. Keep whatever a
lesson actually needs, and use Save Current Layout as Template to capture
your own tuned version once you've found the right balance for a given
class.
