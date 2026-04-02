---
name: hello-world
description: A simple greeting command that demonstrates plugin structure
user-invocable: true
---

# hello-world

Greets the user with a colorful terminal message.

## Usage

Run the hello-world command:

```bash
!`bash "${PLUGIN_DIR}/command.sh"`
```

With a custom name:

```bash
!`bash "${PLUGIN_DIR}/command.sh" --name "${ARGUMENTS}"`
```
