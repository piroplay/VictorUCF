# VictorUCF - Notes de projet Claude Code

## Architecture du projet
- **Type** : Système de template de personnage (pas d'application déployée)
- **Personnage** : Marcus Redingote, coach de crise français, 45 ans
- **Fichiers** : `character.json`, `system-prompt.md`, 7 fichiers KB dans `kb/`
- **Token budget** : ~22KB / ~6000 tokens (compatible tous LLMs modernes)
- **LLM** : Agnostique (Claude, GPT, Gemini, Mistral)
- **TTS/STT** : Conçu mais non implémenté

## Objectif en cours : Intégration Unmute
Donner une voix française grave et naturelle à Victor via Unmute (kyutai-labs/unmute).

### Unmute - Architecture
- 5 services Docker : Frontend (Next.js), Backend (FastAPI/WebSocket), STT (2.5GB VRAM), TTS (5.3GB VRAM), LLM (6.1GB VRAM)
- Total VRAM : ~13.9GB -> rentre dans la RTX A4500 (20GB)
- WebSocket basé sur OpenAI Realtime API (pas 100% compatible)
- Voix françaises disponibles : Charles, Développeuse, Fabieng
- LLM recommandé : Mistral Small 3.2 24B via VLLM

### Configuration Shadow PC
- GPU : RTX A4500 ~20GB VRAM
- RAM : 28GB
- CPU : AMD EPYC 8 coeurs
- OS : Windows 11 Home 10.0.22631

### Plan d'installation (étapes)

1. **Installer WSL2 avec Ubuntu** [EN COURS — BLOCAGE HYPER-V]
   - `wsl --install --no-distribution` : FAIT
   - WSL 2.6.3 installé, version par défaut = 2
   - Features Windows activées (vérifié PowerShell admin) :
     - VirtualMachinePlatform : **Enabled** (confirmé via `Get-WindowsOptionalFeature`)
     - Microsoft-Windows-Subsystem-Linux : **Enabled** (confirmé)
   - 1er redémarrage : FAIT
   - `wsl --install -d Ubuntu` : **ECHEC** — erreur `HCS_E_HYPERV_NOT_INSTALLED`
   - **Cause** : Windows 11 Home n'inclut pas Hyper-V complet, et Shadow PC = VM (nested virtualization)
   - `HyperVisorPresent: True` (vérifié via `Get-ComputerInfo`) → l'hyperviseur est exposé
   - **Solution en cours** (PowerShell admin) :
     1. `bcdedit /set hypervisorlaunchtype auto` ← A EXECUTER
     2. Redémarrer (`shutdown /r /t 0`)
     3. Retester `wsl --install -d Ubuntu`
   - **Si échec après bcdedit** : activer Hyper-V sur Home via script DISM :
     ```
     DISM /Online /Enable-Feature /All /FeatureName:Microsoft-Hyper-V
     ```
     (Puis redémarrer et retester)
   - **Commandes utiles pour debug** (PowerShell admin) :
     - `Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform`
     - `Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`
     - `Get-ComputerInfo -Property HyperVisorPresent`
     - `wsl --status` / `wsl --version` / `wsl -l -v`
   - **Note PATH** : `dism` n'est pas dans le PATH → utiliser chemin complet `C:\Windows\System32\Dism.exe` ou cmdlet PowerShell

2. **Installer Docker + NVIDIA Container Toolkit dans WSL**
   - Docker Engine + Docker Compose
   - NVIDIA Container Toolkit
   - Test : `sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi`

3. **Cloner et configurer Unmute dans WSL**
   - `git clone https://github.com/kyutai-labs/unmute.git ~/unmute`
   - Configurer docker-compose.yml avec Mistral Small 3.2
   - Configurer voices.yaml avec voix française grave (base "Charles")
   - Token HuggingFace : A DEMANDER à l'utilisateur
   - `docker compose up`

4. **Intégrer VictorUCF avec Unmute**
   - Injecter system-prompt.md + KB dans le system prompt Unmute
   - Créer voix "Victor" dans voices.yaml
   - Paramètres vocaux de character.json :
     - langue: fr-FR
     - ton: rauque, grave, posé avec accélérations soudaines
     - rythme: silence long puis frappe chirurgicale
     - registre: direct, court, sujet-verbe-complément

5. **Tester Victor vocal**
   - Latence cible : ~750ms (single GPU)
   - Vérifier voix grave, naturelle, française

### Voix Victor - Spécifications (de character.json)
```json
{
  "language": "fr-FR",
  "tone": "rauque, grave, posé avec des accélérations soudaines",
  "register": "direct, court, sujet-verbe-complément",
  "rhythm": "silence long puis frappe chirurgicale",
  "signature_laugh": "petit rire rauque au fond de la gorge, très bref"
}
```

### Contraintes
- Tout dans WSL, ne pas toucher au système Windows
- GPU single : RTX A4500 20GB VRAM
- Langue : français obligatoire
- Voix : masculine, grave, naturelle

### LLM params (de character.json transpiler_hints)
```json
{
  "temperature": 0.88,
  "top_p": 0.92,
  "frequency_penalty": 0.35,
  "presence_penalty": 0.45,
  "max_tokens_response": 300
}
```
