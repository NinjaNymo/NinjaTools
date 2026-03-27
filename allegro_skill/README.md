# Usage
OrCAD/Allegro PCB Designer use a `allegro.ilinit` file to load skill scripts when launching the tool.

Typically, the file exists under `C:\Cadence\User_Setup`, but this may vary depending on company configuration.

By default, `allegro.ilinit` will look for any `.il` filess in `C:\Cadence\User_Setup\skill` and `load` them:

```
;makes sure the directory exists
;load all files in Skill path
when(isDir("./skill")
	(foreach file (rexMatchList "\\.il$" (getDirFiles "./skill"))
		printf("Loading Skill file: %s\n" file)
		(load strcat("./skill/" file))
	)
)
```

## Pointing `allegro.ilinit` to a Custom Folder
### 1. Creating a User Variable
The following command will create the user variable `NINJA_SKILL` pointing to the directory of which the command was run:
```
setx NINJA_SKILL "%CD%"
```
(It's also possible to do this manually through Windows' Environment Variables.)

### 2. Modify `allegro.ilinit`

**Below the existing lines** in `allegro.ilinit`, add the following:

```
; Load from custom repository path via environment variable
let((customPath)
    ; Get the environment variable
    customPath = getShellEnvVar("NINJA_SKILL")
    
    when(customPath && isDir(customPath)
        printf("Loading Skill files from %s\n" customPath)
        (foreach file (rexMatchList "\\.il$" (getDirFiles customPath))
            printf("Loading Skill file: %s\n" file)
            (load strcat(customPath "/" file))
        )
    )
)
```


# Verify
If this works out, OrCAD/Allegro PCB Designer should spit out the following on launch:

```
Loading Skill files from C:\ninjatools\allegro_skill
```
(Where the path matches the directory where the user variable was set.)