param(
    [switch]$SmokeTest,
    [switch]$SelfTest,
    [switch]$TranscribeTest,
    [switch]$DownloadModel,
    [string]$Model = "small",
    [string]$AudioPath = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtimeRoot = Join-Path $projectRoot "dist\PinkCatAudioCutter\_internal"
$pythonDll = Join-Path $runtimeRoot "python311.dll"
$scriptPath = Join-Path $projectRoot "cat_audio_cutter.pyw"
$buildRoot = Join-Path $projectRoot "build\PinkCatAudioCutter"
$pyzPath = Join-Path $buildRoot "PYZ-00.pyz"
$localPycs = Join-Path $buildRoot "localpycs"

if (!(Test-Path $pythonDll)) {
    throw "Missing bundled Python runtime: $pythonDll"
}

if (!(Test-Path $scriptPath)) {
    throw "Missing app script: $scriptPath"
}

if (!(Test-Path $pyzPath)) {
    throw "Missing PyInstaller PYZ archive: $pyzPath"
}

$env:PYTHONHOME = $runtimeRoot
$env:PYTHONPATH = "$runtimeRoot\base_library.zip;$runtimeRoot;$localPycs;$projectRoot"
$env:PATH = "$runtimeRoot;$runtimeRoot\av.libs;$runtimeRoot\numpy.libs;$runtimeRoot\pywin32_system32;" + $env:PATH
$env:TCL_LIBRARY = "$runtimeRoot\_tcl_data"
$env:TK_LIBRARY = "$runtimeRoot\_tk_data"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class PyBridge {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool SetDllDirectory(string lpPathName);

    [DllImport("python311.dll", CallingConvention = CallingConvention.Cdecl)]
    public static extern int Py_Main(int argc, IntPtr argv);
}
"@

[PyBridge]::SetDllDirectory($runtimeRoot) | Out-Null

if ($SmokeTest) {
    $argsList = @(
        "python",
        "-c",
        @"
import os
import sys
import _frozen_importlib
import pyimod01_archive
pyz_path = r'$pyzPath'
runtime_root = r'$runtimeRoot'
for dll_dir in (runtime_root, os.path.join(runtime_root, 'av.libs'), os.path.join(runtime_root, 'numpy.libs')):
    if os.path.isdir(dll_dir) and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dll_dir)
reader = pyimod01_archive.ZlibArchiveReader(pyz_path)
class PyzLoader:
    def __init__(self, archive_reader):
        self.archive_reader = archive_reader
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.archive_reader.toc:
            return None
        item_type = self.archive_reader.toc[fullname][0]
        is_package = fullname == 'tkinter' or item_type in (pyimod01_archive.PYZ_ITEM_PKG, pyimod01_archive.PYZ_ITEM_NSPKG)
        spec = _frozen_importlib.ModuleSpec(fullname, self, is_package=is_package)
        spec.origin = '<pyz>'
        return spec
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        code = self.archive_reader.extract(module.__spec__.name)
        module.__file__ = f"<pyz:{module.__spec__.name}>"
        if module.__spec__.submodule_search_locations is not None:
            package_dir = os.path.join(runtime_root, *module.__spec__.name.split('.'))
            module.__path__ = [package_dir, module.__spec__.name] if os.path.isdir(package_dir) else [module.__spec__.name]
            module.__package__ = module.__spec__.name
        else:
            module.__package__ = module.__spec__.parent
        exec(code, module.__dict__)
sys.meta_path.insert(0, PyzLoader(reader))
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import pyautogui
import pyperclip
import faster_whisper
with open(r'$scriptPath', 'rb') as handle:
    compile(handle.read(), r'$scriptPath', 'exec')
print('SMOKE_OK')
"@
    )
} elseif ($SelfTest) {
    $argsList = @(
        "python",
        "-c",
        @"
import os
import sys
import _frozen_importlib
import pyimod01_archive
pyz_path = r'$pyzPath'
script_path = r'$scriptPath'
project_root = r'$projectRoot'
runtime_root = r'$runtimeRoot'
for dll_dir in (runtime_root, os.path.join(runtime_root, 'av.libs'), os.path.join(runtime_root, 'numpy.libs')):
    if os.path.isdir(dll_dir) and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dll_dir)
reader = pyimod01_archive.ZlibArchiveReader(pyz_path)
class PyzLoader:
    def __init__(self, archive_reader):
        self.archive_reader = archive_reader
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.archive_reader.toc:
            return None
        item_type = self.archive_reader.toc[fullname][0]
        is_package = fullname == 'tkinter' or item_type in (pyimod01_archive.PYZ_ITEM_PKG, pyimod01_archive.PYZ_ITEM_NSPKG)
        spec = _frozen_importlib.ModuleSpec(fullname, self, is_package=is_package)
        spec.origin = '<pyz>'
        return spec
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        code = self.archive_reader.extract(module.__spec__.name)
        module.__file__ = f"<pyz:{module.__spec__.name}>"
        if module.__spec__.submodule_search_locations is not None:
            package_dir = os.path.join(runtime_root, *module.__spec__.name.split('.'))
            module.__path__ = [package_dir, module.__spec__.name] if os.path.isdir(package_dir) else [module.__spec__.name]
            module.__package__ = module.__spec__.name
        else:
            module.__package__ = module.__spec__.parent
        exec(code, module.__dict__)
sys.meta_path.insert(0, PyzLoader(reader))
import shutil
with open(script_path, 'rb') as handle:
    source = handle.read()
globals_dict = {'__name__': 'cat_audio_cutter_selftest', '__file__': script_path}
exec(compile(source, script_path, 'exec'), globals_dict)
test_root = os.path.join(project_root, 'tmp_selftest')
input_dir = os.path.join(test_root, 'input')
temp_dir = os.path.join(test_root, 'segments')
output_dir = os.path.join(test_root, 'output')
shutil.rmtree(test_root, ignore_errors=True)
os.makedirs(input_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
audio_path = os.path.join(input_dir, 'tone.wav')
globals_dict['run_command']([
    'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=4',
    '-ar', '44100', audio_path,
])
plan = globals_dict['build_segment_plan']('count', audio_path, 2, '')
split_paths = globals_dict['split_audio_file'](audio_path, plan, temp_dir, 'mp3', '64k', '44100', lambda current, total: None)
copied = globals_dict['copy_results_to_folder'](split_paths, output_dir)
if len(copied) != 2 or not all(os.path.exists(path) and os.path.getsize(path) > 0 for path in copied):
    raise RuntimeError('self-test did not create two valid audio segments')
full_paths = globals_dict['export_full_audio_file'](audio_path, temp_dir, 'mp3', '64k', '44100', lambda current, total: None)
if len(full_paths) != 1 or not os.path.exists(full_paths[0]) or os.path.getsize(full_paths[0]) <= 0:
    raise RuntimeError('self-test did not create a valid no-cut audio export')
prepared = globals_dict['prepare_audio_for_local_transcription'](split_paths[0], temp_dir, 1)
if not os.path.exists(prepared) or os.path.getsize(prepared) == 0:
    raise RuntimeError('self-test did not create a valid transcription WAV')
body, content_type = globals_dict['encode_multipart_form']({'model': 'test-model'}, 'file', copied[0])
if b'test-model' not in body or 'multipart/form-data' not in content_type:
    raise RuntimeError('self-test multipart encoding failed')
text = globals_dict['extract_transcript_text']('{"text":"שלום"}')
if text != 'שלום':
    raise RuntimeError('self-test transcript parser failed')
repo_id = globals_dict['resolve_faster_whisper_repo_id']('small')
if repo_id != 'Systran/faster-whisper-small':
    raise RuntimeError('self-test local model resolver failed')
gemini_url = globals_dict['build_gemini_generate_content_url'](
    globals_dict['DEFAULT_GEMINI_TRANSCRIPTION_URL'],
    'gemini-flash-latest',
)
if 'gemini-flash-latest:generateContent' not in gemini_url:
    raise RuntimeError('self-test Gemini URL builder failed')
gemini_fix_payload = globals_dict['build_gemini_text_fix_payload']('bad transcript text')
if 'bad transcript text' not in gemini_fix_payload['contents'][0]['parts'][0]['text']:
    raise RuntimeError('self-test Gemini text-fix payload builder failed')
gemini_summary_payload = globals_dict['build_gemini_summary_payload']('meeting transcript text')
if 'meeting transcript text' not in gemini_summary_payload['contents'][0]['parts'][0]['text']:
    raise RuntimeError('self-test Gemini summary payload builder failed')
gemini_text = globals_dict['extract_gemini_transcript_text']('{"candidates":[{"content":{"parts":[{"text":"hello from gemini"}]}}]}')
if 'hello from gemini' not in gemini_text:
    raise RuntimeError('self-test Gemini response parser failed')
chat_payload = globals_dict['build_openrouter_chat_payload']('fix this transcript', 'openrouter/auto')
if chat_payload.get('model') != 'openrouter/auto' or chat_payload['messages'][0]['content'] != 'fix this transcript':
    raise RuntimeError('self-test chat payload builder failed')
if globals_dict['DEFAULT_EXTERNAL_TRANSCRIPTION_URL'] != 'https://api.openai.com/v1/chat/completions':
    raise RuntimeError('self-test external text endpoint default failed')
chat_text = globals_dict['extract_chat_completion_text']('{"choices":[{"message":{"content":"hello from chat"}}]}')
if chat_text != 'hello from chat':
    raise RuntimeError('self-test chat completion parser failed')
api_keys = globals_dict['parse_api_key_lines']('key-a\n# comment\nkey-b,key-a')
if api_keys != ['key-a', 'key-b']:
    raise RuntimeError('self-test API key parser failed')
shutil.rmtree(test_root, ignore_errors=True)
print('SELFTEST_OK')
"@
    )
} elseif ($TranscribeTest) {
    $argsList = @(
        "python",
        "-c",
        @"
import os
import sys
import _frozen_importlib
import pyimod01_archive
pyz_path = r'$pyzPath'
script_path = r'$scriptPath'
project_root = r'$projectRoot'
runtime_root = r'$runtimeRoot'
model_name = r'$Model'
external_audio_path = r'$AudioPath'
for dll_dir in (runtime_root, os.path.join(runtime_root, 'av.libs'), os.path.join(runtime_root, 'numpy.libs')):
    if os.path.isdir(dll_dir) and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dll_dir)
reader = pyimod01_archive.ZlibArchiveReader(pyz_path)
class PyzLoader:
    def __init__(self, archive_reader):
        self.archive_reader = archive_reader
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.archive_reader.toc:
            return None
        item_type = self.archive_reader.toc[fullname][0]
        is_package = fullname == 'tkinter' or item_type in (pyimod01_archive.PYZ_ITEM_PKG, pyimod01_archive.PYZ_ITEM_NSPKG)
        spec = _frozen_importlib.ModuleSpec(fullname, self, is_package=is_package)
        spec.origin = '<pyz>'
        return spec
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        code = self.archive_reader.extract(module.__spec__.name)
        module.__file__ = f"<pyz:{module.__spec__.name}>"
        if module.__spec__.submodule_search_locations is not None:
            package_dir = os.path.join(runtime_root, *module.__spec__.name.split('.'))
            module.__path__ = [package_dir, module.__spec__.name] if os.path.isdir(package_dir) else [module.__spec__.name]
            module.__package__ = module.__spec__.name
        else:
            module.__package__ = module.__spec__.parent
        exec(code, module.__dict__)
sys.meta_path.insert(0, PyzLoader(reader))
import shutil
with open(script_path, 'rb') as handle:
    source = handle.read()
globals_dict = {'__name__': 'cat_audio_cutter_transcribe_test', '__file__': script_path}
exec(compile(source, script_path, 'exec'), globals_dict)
test_root = os.path.join(project_root, 'tmp_transcribe_test')
input_dir = os.path.join(test_root, 'input')
temp_dir = os.path.join(test_root, 'segments')
output_dir = os.path.join(test_root, 'output')
shutil.rmtree(test_root, ignore_errors=True)
os.makedirs(input_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
if external_audio_path:
    if not os.path.exists(external_audio_path):
        raise RuntimeError('AudioPath does not exist: ' + external_audio_path)
    split_paths = [external_audio_path]
else:
    audio_path = os.path.join(input_dir, 'tone.wav')
    globals_dict['run_command']([
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1.2',
        '-ar', '44100', audio_path,
    ])
    plan = globals_dict['build_segment_plan']('count', audio_path, 2, '')
    split_paths = globals_dict['split_audio_file'](audio_path, plan, temp_dir, 'mp3', '64k', '44100', lambda current, total: None)
def report_segment(current, total, label):
    print(label, flush=True)
def report_model(label, percent=None):
    print(label if percent is None else f"{label} [{percent:.0f}%]", flush=True)
transcript_files, transcript_text, transcript_path = globals_dict['transcribe_audio_files_locally'](
    split_paths,
    output_dir,
    model_name,
    report_segment,
    report_model,
    temp_dir,
)
if not os.path.exists(transcript_path):
    raise RuntimeError('transcribe-test did not create transcript_all_segments.txt')
if os.path.getsize(transcript_path) == 0:
    raise RuntimeError('transcribe-test created an empty transcript file')
print('TRANSCRIPT_PATH=' + transcript_path, flush=True)
if not external_audio_path:
    shutil.rmtree(test_root, ignore_errors=True)
print('TRANSCRIBE_TEST_OK')
"@
    )
} elseif ($DownloadModel) {
    $argsList = @(
        "python",
        "-c",
        @"
import os
import sys
import _frozen_importlib
import pyimod01_archive
pyz_path = r'$pyzPath'
script_path = r'$scriptPath'
runtime_root = r'$runtimeRoot'
model_name = r'$Model'
for dll_dir in (runtime_root, os.path.join(runtime_root, 'av.libs'), os.path.join(runtime_root, 'numpy.libs')):
    if os.path.isdir(dll_dir) and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dll_dir)
reader = pyimod01_archive.ZlibArchiveReader(pyz_path)
class PyzLoader:
    def __init__(self, archive_reader):
        self.archive_reader = archive_reader
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.archive_reader.toc:
            return None
        item_type = self.archive_reader.toc[fullname][0]
        is_package = fullname == 'tkinter' or item_type in (pyimod01_archive.PYZ_ITEM_PKG, pyimod01_archive.PYZ_ITEM_NSPKG)
        spec = _frozen_importlib.ModuleSpec(fullname, self, is_package=is_package)
        spec.origin = '<pyz>'
        return spec
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        code = self.archive_reader.extract(module.__spec__.name)
        module.__file__ = f"<pyz:{module.__spec__.name}>"
        if module.__spec__.submodule_search_locations is not None:
            package_dir = os.path.join(runtime_root, *module.__spec__.name.split('.'))
            module.__path__ = [package_dir, module.__spec__.name] if os.path.isdir(package_dir) else [module.__spec__.name]
            module.__package__ = module.__spec__.name
        else:
            module.__package__ = module.__spec__.parent
        exec(code, module.__dict__)
sys.meta_path.insert(0, PyzLoader(reader))
with open(script_path, 'rb') as handle:
    source = handle.read()
globals_dict = {'__name__': 'cat_audio_cutter_model_download', '__file__': script_path}
exec(compile(source, script_path, 'exec'), globals_dict)
print('Downloading model: ' + model_name, flush=True)
def report(label, percent=None):
    if percent is None:
        print(label, flush=True)
    else:
        print(f"{label} [{percent:.0f}%]", flush=True)
model_path = globals_dict['ensure_faster_whisper_model'](model_name, report)
print('MODEL_DOWNLOAD_OK', flush=True)
print(model_path, flush=True)
"@
    )
} else {
    $argsList = @(
        "python",
        "-c",
        @"
import os
import sys
import _frozen_importlib
import pyimod01_archive
pyz_path = r'$pyzPath'
script_path = r'$scriptPath'
runtime_root = r'$runtimeRoot'
for dll_dir in (runtime_root, os.path.join(runtime_root, 'av.libs'), os.path.join(runtime_root, 'numpy.libs')):
    if os.path.isdir(dll_dir) and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dll_dir)
reader = pyimod01_archive.ZlibArchiveReader(pyz_path)
class PyzLoader:
    def __init__(self, archive_reader):
        self.archive_reader = archive_reader
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.archive_reader.toc:
            return None
        item_type = self.archive_reader.toc[fullname][0]
        is_package = fullname == 'tkinter' or item_type in (pyimod01_archive.PYZ_ITEM_PKG, pyimod01_archive.PYZ_ITEM_NSPKG)
        spec = _frozen_importlib.ModuleSpec(fullname, self, is_package=is_package)
        spec.origin = '<pyz>'
        return spec
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        code = self.archive_reader.extract(module.__spec__.name)
        module.__file__ = f"<pyz:{module.__spec__.name}>"
        if module.__spec__.submodule_search_locations is not None:
            package_dir = os.path.join(runtime_root, *module.__spec__.name.split('.'))
            module.__path__ = [package_dir, module.__spec__.name] if os.path.isdir(package_dir) else [module.__spec__.name]
            module.__package__ = module.__spec__.name
        else:
            module.__package__ = module.__spec__.parent
        exec(code, module.__dict__)
sys.meta_path.insert(0, PyzLoader(reader))
with open(script_path, 'rb') as handle:
    source = handle.read()
globals_dict = {'__name__': '__main__', '__file__': script_path}
exec(compile(source, script_path, 'exec'), globals_dict)
"@
    )
}

$ptrs = New-Object System.IntPtr[] ($argsList.Count)
$argv = [System.IntPtr]::Zero

try {
    for ($i = 0; $i -lt $argsList.Count; $i++) {
        $ptrs[$i] = [System.Runtime.InteropServices.Marshal]::StringToHGlobalUni($argsList[$i])
    }

    $argv = [System.Runtime.InteropServices.Marshal]::AllocHGlobal([System.IntPtr]::Size * $argsList.Count)
    for ($i = 0; $i -lt $argsList.Count; $i++) {
        [System.Runtime.InteropServices.Marshal]::WriteIntPtr($argv, $i * [System.IntPtr]::Size, $ptrs[$i])
    }

    $exitCode = [PyBridge]::Py_Main($argsList.Count, $argv)
    exit $exitCode
}
finally {
    for ($i = 0; $i -lt $ptrs.Length; $i++) {
        if ($ptrs[$i] -ne [System.IntPtr]::Zero) {
            [System.Runtime.InteropServices.Marshal]::FreeHGlobal($ptrs[$i])
        }
    }

    if ($argv -ne [System.IntPtr]::Zero) {
        [System.Runtime.InteropServices.Marshal]::FreeHGlobal($argv)
    }
}
