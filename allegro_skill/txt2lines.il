; Convert Text to Lines in Allegro PCB Designer
; Uses axlText2Lines to convert text objects to actual line segments
; v3: Uses the text's original layer as default target

println("txt2lines.il...")

defun(convertText ()
  let((text lines layer flattened selset defaultLayer promptMsg)
    ; Set filter to select only text
    axlSetFindFilter(?enabled '("TEXT") ?onButtons '("TEXT"))

    ; Clear any previous selection
    axlClearSelSet()

    ; Prompt user to select text using point selection
    axlUIWPrint(nil "Click on text to convert to lines")

    ; Use axlSingleSelectPoint for interactive selection
    if(axlSingleSelectPoint() then
      ; Get the selected object
      selset = axlGetSelSet()
      text = car(selset)

      if(text && text->objType == "text" then
        ; Get the layer of the selected text as default
        ; Text layer is stored in the layer property
        defaultLayer = text->layer

        ; Show current text layer to user
        axlUIWPrint(nil sprintf(nil "Text is on layer: %s" defaultLayer))

        ; Ask for target layer with the text's layer as default
        promptMsg = sprintf(nil "Enter target layer (press Enter for %s):" defaultLayer)
        layer = axlUIPrompt(promptMsg)

        ; Use text's layer if no layer specified (user just pressed Enter)
        when(!layer || layer == "" layer = defaultLayer)

        ; Convert text to lines using built-in function
        lines = axlText2Lines(text)

        if(lines then
          ; Flatten the nested list structure
          flattened = nil
          foreach(charList lines
            foreach(path charList
              flattened = cons(path flattened)
            )
          )

          ; Create line segments on the specified layer
          foreach(path flattened
            axlDBCreatePath(path layer nil)
          )

          axlUIWPrint(nil sprintf(nil "Created %d line segments on layer %s" length(flattened) layer))

          ; Ask if user wants to delete original text
          if(axlUIYesNo("Delete original text?") then
            axlDeleteObject(text)
          )
        else
          axlUIWPrint(nil "Could not convert text (may be empty)")
        )
      else
        axlUIWPrint(nil "Selected object is not text")
      )
    else
      axlUIWPrint(nil "No object selected")
    )

    ; Clear selection when done
    axlClearSelSet()
  )
)

; Register the command
axlCmdRegister("txt2lines" 'convertText)

;println("Command registered: type 'txt2lines' to convert text to lines")