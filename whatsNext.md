# Further development

## Next steps

- page title ✅

- display the song titles properly ✅

- scores: changes to settings only when user releases the slider, not in "real time" ✅

- fetch performances from repo API ✅

- display performances in rudimentary fashion (simple tables for now?) ✅

## In the middle term

- enable viewing annot tags by clicking/hovering on them, opening a little window or the like

    - clicking on notes: info
        - accidentals: add flat, sharp, natural where necessary

    - handling add tags: check whether source="dwdfdc9075d0e-7aaa-4a82-bfa0-06eb81584587"; find g tag, find corresponding add tag, check source attribute
        - if yes, add an attribute (id, class) to the corresponding g tag in svg ==> use this to style in CSS
        - if add is clicked, display information: medium, unclear? reason?, type, label


- do the actual work of generating visualizations in the backend or the frontend?

- how will I visualize the performances? talk to Joshua

## Long-term

- use "real" github repo as source instead of test db

- host the app at some point? (using academy infrastructure perhaps)



