# Using LOUIM in Primary Schools

Young learners benefit the most from a small, stable menu bar. Reading
eleven menu labels is itself a task before a seven-year-old gets to "insert
a picture." Here are a few notes for this age group specifically, on top of
the general [teacher guide](../teacher-guide.md).

## Start smaller than level-1 if needed

The bundled `writer-level-1` keeps File, Edit, Format, and Help. That's
still four menus and a formatting toolbar. For very early primary use it's
common to go further. Configure Menus can drop Format too, leaving just
File, Edit, and Help, if a lesson is purely about typing words and saving.
Save the result as your own template, something like
`writer-primary-1.louim`, rather than editing the bundled file, so the
original starter templates stay available as a reference.

## Icons over menu digging

Primary learners often navigate by toolbar icon before they can reliably
read menu labels. Setting `"hide_toolbar_buttons_with_menus": true`, already
set in the bundled templates, keeps the toolbar in sync with whatever menus
are hidden, so a young learner never sees a toolbar icon for a feature whose
menu has disappeared. That kind of mismatch, where a button looks familiar
but stops working the way it used to, is worth avoiding deliberately at this
age.

## One class, one shared template

Rather than customizing per student, most primary classrooms get the most
value from one shared template applied at the start of each session.
Consistency matters more than individual pacing at this age, and switching
everyone with Choose Template takes seconds. Save it to `Documents/LOUIM
templates` on the classroom machines so it survives between sessions and
LibreOffice updates.

## Restore is the safety net, not a threat

If a young learner, or a curious click, ends up somewhere unexpected,
Restore Full Menus always gets back to a known state. Nothing is ever lost,
since LOUIM only ever hides interface, never content or files. It's worth
telling students this directly: LOUIM changing what they can see isn't a
punishment or a lock, and a teacher, or eventually the student, can always
bring everything back.
