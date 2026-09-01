# Designing Progressive Writer Courses

Here's a practical pattern for sequencing a Writer course around LOUIM's
templates, building on the bundled `writer-level-1`, `writer-level-2`, and
`writer-full` starting point. See the [teacher guide](../teacher-guide.md)
for what each one hides.

## A three-stage skeleton

Stage one, Getting Started (`writer-level-1`), keeps only File, Edit,
Format, and Help. View, Insert, Table, and Tools are hidden, along with the
Find and Insert toolbars, while Drawing stays visible. This suits typing,
basic formatting like bold and italic, and saving and opening files. A
learner here isn't yet choosing from eleven menus, just four.

Stage two, Basic Editing (`writer-level-2`), re-adds View, Insert, and
Table, while Format ▸ Styles and Tools stay hidden. Once a class is
comfortable with paragraphs and formatting, this is a good point to
introduce inserting images and tables and using View, for formatting marks
or zoom, without yet exposing Tools ▸ Options, Macros, or the Styles system.

Stage three, Complete Writer (`writer-full`), shows everything. It's
equivalent to Restore Full Menus. Use it once a course's foundational skills
are established and the goal shifts to full independent use.

## Adjusting the skeleton for your course

The bundled three levels are a reasonable default, not a fixed curriculum.
There are two ways to adapt without writing JSON by hand. Configure Menus,
then Save works for a quick variant. A course that wants Table available
from day one but not Insert, for example, can untick just Insert, leave
Table ticked, and save as `writer-level-1b.louim`. Save Current Layout as
Template, after tuning toolbars or the sidebar by hand through Tools ▸
Customize and the sidebar's own menu, suits a stage that needs more than
whole-menu control, such as hiding only the Insert ▸ Chart toolbar button
while keeping the rest of Insert.

## Sequencing across a term

Because applying is always non-cumulative and Restore always gets back to
the true defaults, moving a class between stages mid-term is a single Choose
Template click in either direction. There's no risk of a half-old,
half-new interface, and no need to reset before switching. That makes it
practical to keep several named stage templates, `writer-level-1`,
`writer-level-1b`, `writer-level-2`, and so on, in `Documents/LOUIM
templates`, and move a class or an individual student between them as the
course progresses rather than designing one interface and living with it
for the whole term.
