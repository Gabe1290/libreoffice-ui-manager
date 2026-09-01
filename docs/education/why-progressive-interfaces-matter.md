# Why Progressive Interfaces Matter

LibreOffice Writer's default menu bar has eleven top-level menus and over 550
commands. A learner opening it for the first time doesn't need to know that
File contains Send, or that Format has a Styles submenu, or what Tools ▸
Macros does. But all of it is there, all at once, competing for attention
with the one or two things the current lesson is actually about.

LOUIM's premise, stated in [VISION.md](../../VISION.md), is that the
interface should adapt to the learner rather than the other way around.
Concretely, that means a teacher decides what's visible at each stage of a
course, rather than leaving a learner to visually filter the whole
application down to what matters today.

## What this looks like with LOUIM specifically

Configure Menus lets a teacher remove file-level clutter for a first lesson
in under a minute. Untick View, Insert, Table, and Tools, and the menu bar
goes from eleven menus to four. See the [teacher guide](../teacher-guide.md)
for the walkthrough. The bundled `*-level-1.louim` templates already encode a
reasonable first cut for each app, so getting started doesn't require
designing an interface from scratch. And because a hidden feature is one
Restore Full Menus click away, simplifying an interface doesn't mean locking
it down. See
[reducing-cognitive-load.md](reducing-cognitive-load.md) for more on that
distinction.

## Not a lockdown tool

Progressive disclosure is a teaching technique, not an access-control
mechanism. LOUIM has no concept of a password-protected profile a student
can't escape. A curious student who opens Tools ▸ Extension Manager, or asks
a teacher to click Restore Full Menus, can always get to the whole
application. The goal is to reduce what's competing for attention, not what's
reachable.
