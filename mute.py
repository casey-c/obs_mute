#
# Project     OBS Mute Indicator Script
# @author     David Madison, Casey Conway
# @link       github.com/casey-c/obs_mute
# @license    GPLv3 - Copyright (c) 2020 David Madison, Casey Conway
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import obspython as obs

# ------------------------------------------------------------

# Script Properties

audio_source_name = ""  # source name to monitor, stored from properties
image_source_name = ""  # source name to monitor, stored from properties

# Constants

init_state_delay = 1600  # ms before sending initial state (wait for device startup)

# Global Variables

sources_loaded = False  # set to 'True' when sources are presumed loaded
callback_name = None  # source name for the current callback

# ------------------------------------------------------------

def get_scene():
	src = obs.obs_frontend_get_current_scene()
	scene = obs.obs_scene_from_source(src)
	obs.obs_source_release(src)
	return scene

def set_visibility(val):
	scene = get_scene()
	#source = obs.obs_get_source_by_name(image_source_name)
	source = obs.obs_scene_find_source(scene, image_source_name)
	obs.obs_sceneitem_set_visible(source, val)

def callback(muted):
	set_visibility(muted)
	output = "muted" if muted else "unmuted"
	print(output)
	#write_to_file(output)

def send_initial_state():
	muted = get_muted(audio_source_name)
	callback(muted)
	obs.remove_current_callback()  # remove this one-shot timer


def get_muted(sn):
	source = obs.obs_get_source_by_name(sn)

	if source is None:
		return None

	muted = obs.obs_source_muted(source)
	obs.obs_source_release(source)

	return muted


def mute_callback(calldata):
	muted = obs.calldata_bool(calldata, "muted")  # true if muted, false if not
	callback(muted)


def test_mute(prop, props):
	callback(True)


def test_unmute(prop, props):
	callback(False)


def create_muted_callback(sn):
	global callback_name

	if sn is None or sn == callback_name:
		return False # source hasn't changed or callback is already set

	if callback_name is not None:
		remove_muted_callback(callback_name)

	source = obs.obs_get_source_by_name(sn)

	if source is None:
		return False

	handler = obs.obs_source_get_signal_handler(source)
	obs.signal_handler_connect(handler, "mute", mute_callback)
	callback_name = sn  # save name for future reference

	obs.obs_source_release(source)

	return True


def remove_muted_callback(sn):
	if sn is None:
		return False # no callback is set

	source = obs.obs_get_source_by_name(sn)

	if source is None:
		return False

	handler = obs.obs_source_get_signal_handler(source)
	obs.signal_handler_disconnect(handler, "mute", mute_callback)

	obs.obs_source_release(source)

	return True


def list_audio_sources():
	audio_sources = []
	sources = obs.obs_enum_sources()

	for source in sources:
		if obs.obs_source_get_type(source) == obs.OBS_SOURCE_TYPE_INPUT:
			capabilities = obs.obs_source_get_output_flags(source)

			has_audio = capabilities & obs.OBS_SOURCE_AUDIO

			if has_audio:
				audio_sources.append(obs.obs_source_get_name(source))

	obs.source_list_release(sources)

	return audio_sources

def list_image_sources():
	image_sources = []
	sources = obs.obs_enum_sources()

	for source in sources:
		source_id = obs.obs_source_get_id(source)
		print(source_id)
		if source_id == "image_source":
			image_sources.append(obs.obs_source_get_name(source))

	obs.source_list_release(sources)
	return image_sources


def source_loading():
	global sources_loaded

	source = obs.obs_get_source_by_name(audio_source_name)

	if source and create_muted_callback(audio_source_name):
		sources_loaded = True  #sources loaded, no need for this anymore
		obs.remove_current_callback()  # delete this timer

	obs.obs_source_release(source)

# ------------------------------------------------------------

# OBS Script Functions

def script_description():
	return "<b>OBS Mute Indicator Script</b>" + \
			"<hr>" + \
			"Displays an image while the audio source is muted" + \
			"<br/>" + \
			"https://github.com/casey-c/obs_mute"


def script_update(settings):
	global audio_source_name, image_source_name

	audio_source_name = obs.obs_data_get_string(settings, "audio_source")
	image_source_name = obs.obs_data_get_string(settings, "image_source")

	if sources_loaded:
		create_muted_callback(audio_source_name)  # create 'muted' callback for source


def script_properties():
	props = obs.obs_properties_create()

	# Create list of audio sources and add them to properties list
	audio_sources = list_audio_sources()
	audio_source_list = obs.obs_properties_add_list(props, "audio_source", "Audio Source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

	for name in audio_sources:
		obs.obs_property_list_add_string(audio_source_list, name, name)

    # Create list of image sources and add them to properties list
	image_sources = list_image_sources()
	image_source_list = obs.obs_properties_add_list(props, "image_source", "Image Source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

	for name in image_sources:
		obs.obs_property_list_add_string(image_source_list, name, name)

	# Add testing buttons and debug toggle
	#obs.obs_properties_add_button(props, "test_mute", "Test Mute", test_mute)
	#obs.obs_properties_add_button(props, "test_unmute", "Test Unmute", test_unmute)

	return props


def script_load(settings):
	obs.timer_add(source_loading, 10)  # brute force - try to load sources every 10 ms until the callback is created


def script_unload():
	obs.timer_remove(source_loading)
	obs.timer_remove(send_initial_state)

	remove_muted_callback(callback_name)  # remove the callback if it exists
