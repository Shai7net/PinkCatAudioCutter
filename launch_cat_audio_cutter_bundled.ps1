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
whatsapp_mp3 = globals_dict['prepare_whatsapp_audio_files'](copied, temp_dir, 'mp3')
whatsapp_ogg = globals_dict['prepare_whatsapp_audio_files'](copied, temp_dir, 'ogg')
if len(whatsapp_mp3) != 2 or not all(path.endswith('.mp3') and os.path.getsize(path) > 0 for path in whatsapp_mp3):
    raise RuntimeError('self-test did not prepare valid WhatsApp MP3 files')
if len(whatsapp_ogg) != 2 or not all(path.endswith('.ogg') and os.path.getsize(path) > 0 for path in whatsapp_ogg):
    raise RuntimeError('self-test did not prepare valid WhatsApp OGG fallback files')
default_whatsapp_bot = globals_dict['get_whatsapp_bot_config']('missing-option')
if default_whatsapp_bot['phone'] != '972559571223':
    raise RuntimeError('self-test WhatsApp bot fallback failed')
composer_point = globals_dict['get_whatsapp_composer_point'](100, 50, 1000, 700)
if composer_point != (400, 708):
    raise RuntimeError('self-test WhatsApp composer position failed')
capture_region = globals_dict['get_whatsapp_capture_region'](100, 50, 1000, 700)
if capture_region != (380, 316, 700, 392):
    raise RuntimeError('self-test WhatsApp capture region failed')
context_paste_point = globals_dict['get_whatsapp_context_paste_point'](100, 50, 1000, 700)
if context_paste_point != (480, 600):
    raise RuntimeError('self-test WhatsApp context-menu paste position failed')
from PIL import Image
unchanged_a = Image.new('RGB', (20, 20), 'white')
unchanged_b = Image.new('RGB', (20, 20), 'white')
changed = Image.new('RGB', (20, 20), 'black')
if globals_dict['calculate_image_change_ratio'](unchanged_a, unchanged_b) != 0:
    raise RuntimeError('self-test WhatsApp unchanged image comparison failed')
if globals_dict['calculate_image_change_ratio'](unchanged_a, changed) < 0.99:
    raise RuntimeError('self-test WhatsApp changed image comparison failed')
if os.environ.get('PINKCAT_CLIPBOARD_TEST') == '1':
    original_clipboard_text = globals_dict['pyperclip'].paste()
    try:
        globals_dict['set_files_to_clipboard'](copied)
        clipboard_paths = globals_dict['get_clipboard_file_paths']()
        expected_paths = {os.path.normcase(os.path.normpath(path)) for path in copied}
        actual_paths = {os.path.normcase(os.path.normpath(path)) for path in clipboard_paths}
        if not expected_paths.issubset(actual_paths):
            raise RuntimeError('self-test native FileDrop clipboard verification failed')
        print('CLIPBOARD_FILEDROP_OK')
    finally:
        globals_dict['pyperclip'].copy(original_clipboard_text)
if os.environ.get('PINKCAT_WHATSAPP_PASTE_TEST') == '1':
    original_clipboard_text = globals_dict['pyperclip'].paste()
    try:
        bot_config = globals_dict['get_whatsapp_bot_config'](globals_dict['DEFAULT_WHATSAPP_BOT_OPTION'])
        globals_dict['automate_whatsapp_send_to_bot']([copied[0]], bot_config['phone'], bot_config['label'])
        print('WHATSAPP_PASTE_OK')
    finally:
        globals_dict['pyautogui'].press('esc')
        globals_dict['pyperclip'].copy(original_clipboard_text)
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
azure_configs = globals_dict['normalize_azure_openai_configs']([
    {
        'api_key': 'azure-key-a',
        'azure_endpoint': 'https://example-resource.openai.azure.com/',
        'deployment_name': 'whisper',
        'api_version': '2024-02-01',
    },
    {
        'api_key': 'azure-key-b',
        'azure_endpoint': 'https://example-resource-b.openai.azure.com',
    },
])
if len(azure_configs) != 2 or azure_configs[0]['azure_endpoint'].endswith('/'):
    raise RuntimeError('self-test Azure config normalizer failed')
azure_url = globals_dict['build_azure_whisper_transcription_url'](azure_configs[0])
if '/openai/deployments/whisper/audio/transcriptions?api-version=2024-02-01' not in azure_url:
    raise RuntimeError('self-test Azure transcription URL builder failed')
attempted_azure_keys = []
def fake_azure_call(config):
    attempted_azure_keys.append(config['api_key'])
    if len(attempted_azure_keys) == 1:
        raise globals_dict['ExternalApiBusyError']('quota')
    return 'azure transcript'
azure_text = globals_dict['call_with_azure_openai_config_pool'](azure_configs, fake_azure_call)
if azure_text != 'azure transcript' or attempted_azure_keys != ['azure-key-a', 'azure-key-b']:
    raise RuntimeError('self-test Azure config failover failed')
if globals_dict['get_transcription_engine_value']('Azure Cloud Whisper') != globals_dict['TRANSCRIPTION_ENGINE_AZURE_OPENAI']:
    raise RuntimeError('self-test transcription engine resolver failed')
app = globals_dict['CatAudioCutterApp']()
app.root.update_idletasks()
if not hasattr(app, 'transcribe_button') or not app.transcribe_button.winfo_exists():
    raise RuntimeError('self-test UI did not create the transcribe action card')
if not hasattr(app, 'player_fill_item'):
    raise RuntimeError('self-test UI did not create the audio player')
if not hasattr(app, 'folder_canvas_item'):
    raise RuntimeError('self-test UI did not create the output folder icon')
if set(app.hotspot_tooltip_texts) != {'upload', 'cut', 'transcribe'}:
    raise RuntimeError('self-test UI did not create all three hover explanations')
if globals_dict['HOVER_TOOLTIP_DELAY_MS'] != 2500 or globals_dict['WHATSAPP_NOTICE_DURATION_MS'] != 4000:
    raise RuntimeError('self-test tooltip/WhatsApp notice timing failed')
app.show_hover_tooltip('tooltip self-test')
app.root.update_idletasks()
if not app.hover_tooltip_window or not app.hover_tooltip_window.winfo_exists():
    raise RuntimeError('self-test hover tooltip did not open')
app.hide_hover_tooltip()
app.show_whatsapp_clipboard_notice({'label': '+000', 'phone': '000'})
app.root.update_idletasks()
if not app.whatsapp_notice_window or not app.whatsapp_notice_window.winfo_exists():
    raise RuntimeError('self-test WhatsApp clipboard notice did not open')
app.whatsapp_notice_window.destroy()
app.whatsapp_notice_window = None
if len(app.whatsapp_bot_combo.cget('values')) < 2:
    raise RuntimeError('self-test UI did not create the WhatsApp bot choices')
if app.settings_notebook.index('end') < 4:
    raise RuntimeError('self-test UI did not create the settings tabs')
app.transcription_engine_var.set('Azure Cloud Whisper')
app.transcription_mode_var.set(globals_dict['TRANSCRIPTION_LOCAL'])
app.settings_notebook.select(2)
app.toggle_transcription_settings()
app.toggle_transcription_engine_settings()
app.root.update_idletasks()
local_model_state = app.local_model_combo.cget('state')
if local_model_state != 'disabled' and not app.local_model_combo.instate(['disabled']):
    raise RuntimeError('self-test UI did not disable the local model selector for Azure engine: ' + str(local_model_state))
if not app.azure_openai_frame.winfo_manager():
    raise RuntimeError('self-test UI did not show Azure settings for Azure engine')
app.azure_endpoint_var.set('https://example-resource.openai.azure.com')
app.azure_deployment_var.set('whisper')
app.azure_api_version_var.set('2024-02-01')
app.azure_api_key_entry.delete('1.0', 'end')
app.azure_api_key_entry.insert('1.0', 'azure-key-ui-a\nazure-key-ui-b')
azure_form_configs = app.get_current_azure_openai_configs()
if len(azure_form_configs) != 2 or azure_form_configs[1]['api_key'] != 'azure-key-ui-b':
    raise RuntimeError('self-test UI did not build Azure configs from form values')
app.transcription_engine_var.set('Local Whisper - \u05d1\u05de\u05d7\u05e9\u05d1')
app.toggle_transcription_engine_settings()
app.root.update_idletasks()
if app.azure_openai_frame.winfo_manager():
    raise RuntimeError('self-test UI did not hide Azure settings for local engine')
app.root.destroy()
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
