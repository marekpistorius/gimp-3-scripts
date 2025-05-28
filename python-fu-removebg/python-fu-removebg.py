#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2024-2026 Marek Pistorius
# This file is part of gimp-python-fu-removebg .
# gimp-python-fu-removebg is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version.
# gimp-python-fu-removebg is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Xfce-nameday-plugin. If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union
import os, sys, string, tempfile, platform
import subprocess

def N_(message): return message
def _(message): return GLib.dgettext(None, message)
tupleModel = ("u2net","u2net_human_seg", "u2net_cloth_seg", "u2netp", "silueta", "isnet-general-use", "isnet-anime", "sam", "birefnet-general" ,"birefnet-general-lite", "birefnet-portrait", "birefnet-dis", "birefnet-hrsod", "birefnet-cod", "birefnet-massive" )

REMBG_BASE_PATH = ""

def find_rembg_install() -> Optional[Path]:

	home = sys.exec_prefix

	possible_paths = []
	# Common installation paths
	if sys.platform == "win32":
		possible_paths = [
			Path("C:/Program Files (x86)/RemBG/"),
			Path("C:/Program Files/RemBG/"),
		]

	for path in possible_paths:
		if path.is_dir():
			return path

	# Fallback to user-configured path if specified
	if REMBG_BASE_PATH and (nik_path := Path(REMBG_BASE_PATH)).is_dir():
		return nik_path

	show_alert(
	text="rembg installation path not found",
		message="Please specify the correct installation path 'REMBG_BASE_PATH' in the script.",
		)

	return None

class PythonRemoveBG(Gimp.PlugIn):
		## GimpPlugIn virtual methods ##
		def do_set_i18n(self, procname):
			return True, 'gimp30-python', None

		def do_query_procedures(self):
			return [ 'python-fu-removebg' ]

		def do_create_procedure(self, name):
			procedure = Gimp.ImageProcedure.new(self, name,
										Gimp.PDBProcType.PLUGIN,
										self.removebg, None)
			procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)
			procedure.set_documentation (_("Remove Background AI"),
										_("Remove Background AI"),
										 name)
			procedure.set_menu_label(_("RemoveBG"))
			procedure.set_attribution("MP",
										"(c) GPL V3.0 or later",
										"2024-2025")
			procedure.add_menu_path('<Image>/Filters/RemoveBG/')

			procedure.add_boolean_argument("asMask","as Mask","As mask",False,GObject.ParamFlags.READWRITE)
			procedure.add_boolean_argument("AlphaMatting","AlphaMatting","AlphaMatting",False,GObject.ParamFlags.READWRITE)
			procedure.add_double_argument("aeValue","aeValue","aeValue",0,100,15 ,GObject.ParamFlags.READWRITE)


			model_choice = Gimp.Choice.new()
			model_choice.add("u2net",0,"u2net","")
			model_choice.add("u2net_human_seg",1,"u2net_human_seg","")
			model_choice.add("u2net_cloth_seg",2,"u2net_cloth_seg","")
			model_choice.add("u2netp",3,"u2netp","")
			model_choice.add("silueta",4,"silueta","")
			model_choice.add("isnet-general-use",5,"isnet-general-use","")
			model_choice.add("isnet-anime",6,"isnet-anime","")
			model_choice.add("sam",7,"sam","")
			model_choice.add("birefnet-general",8,"birefnet-general","")
			model_choice.add("birefnet-cod",9,"birefnet-cod","")
			model_choice.add("birefnet-massive",10,"birefnet-massive","")
			model_choice.add("birefnet-portrait",11,"birefnet-portrait","")
			model_choice.add("birefnet-general-lite",12,"birefnet-general-lite","")
			model_choice.add("birefnet-hrsod",13,"birefnet-hrsod","")
			model_choice.add("birefnet-dis",14,"birefnet-dis","")

			procedure.add_choice_argument ("Model", _("Model"),
                                           _("Model"), model_choice,
                                           "u2net", GObject.ParamFlags.READWRITE)

			return procedure

		def removebg(self, procedure, run_mode, image,  drawables, config, run_data) :
		
			if run_mode == Gimp.RunMode.INTERACTIVE:
			 	GimpUi.init('python-fu-removebg.py')

			 	dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
			 	dialog.fill(None)
			 	if not dialog.run():
			 		dialog.destroy()
			 		return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
			 	else:
			 		dialog.destroy()

			AlphaMatting = config.get_property('AlphaMatting')
			asMask = config.get_property('asMask')
			selModel  = config.get_choice_id("Model") 
			aeValue = config.get_property('aeValue')		

			removeTmpFile = True

			tdir = tempfile.gettempdir()
			print(tdir)
			jpgFileF = "Temp-gimp-0000.jpg"
			jpgFile = os.path.join(tdir,jpgFileF)
			
			pngFileF = "Temp-gimp-0000.png"
			pngFile = os.path.join(tdir,pngFileF)
			

			x1 = 0
			y1 = 0

			option = ""
			
			Gimp.context_pop()
			image.undo_group_start()
			curLayer = image.get_selected_layers()

			fileOut = Gio.File.new_for_path(pngFile)	
			file = Gio.File.new_for_path(jpgFile)	
			f = image.get_file()
			if curLayer[0]:
				if not file.query_exists():
					file.create(Gio.FileCreateFlags.REPLACE_DESTINATION , None)
			else:
				pdb.gimp_edit_copy(drawable)
				non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
				tmpImage = gimp.Image(x2-x1, y2-y1, 0)
				tmpDrawable = gimp.Layer(tmpImage, "Temp", tmpImage.width, tmpImage.height, RGB_IMAGE, 100, NORMAL_MODE)
				pdb.gimp_image_add_layer(tmpImage, tmpDrawable, 0)
				pat = pdb.gimp_context_get_pattern()
				pdb.gimp_context_set_pattern("Leopard")
				pdb.gimp_drawable_fill(tmpDrawable, 4)
				pdb.gimp_context_set_pattern(pat)
				pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(tmpDrawable,TRUE))
				pdb.file_jpeg_save(tmpImage, tmpDrawable, jpgFile, jpgFile, 0.95, 0, 1, 0, "", 0, 1, 0, 0)
				pdb.gimp_image_delete(tmpImage)
	
#			aiExe = Path("C://Program Files (x86)/Rembg/rembg.exe")
			aiExe = str(find_rembg_install())
			aiExe += "/rembg.exe"
						
			if AlphaMatting:
				option = "-a -ae %d" % (aeValue)
			cmd = '%s i -m %s %s "%s" "%s"' % (aiExe, tupleModel[selModel], option, f.get_path(), pngFile)
			print(cmd)

			subprocess.run(cmd)	

			file_exists = os.path.exists(pngFile)
			if file_exists:
				newlayer = Gimp.file_load_layer(run_mode,image,fileOut)
				image.insert_layer(newlayer, None,-1)
			
			if asMask:
				image.select_item(Gimp.ChannelOps.REPLACE, newlayer)
				copyLayer = newlayer.copy()
				image.remove_layer(newlayer)
				image.insert_layer(copyLayer,None, -1)
				mask = copyLayer.create_mask(Gimp.AddMaskType.SELECTION)
				copyLayer.add_mask(mask)
				image.get_selection().none(image)

			image.undo_group_end()
			Gimp.displays_flush()

			if removeTmpFile:
				if file.query_exists():
					file.delete()
				if fileOut.query_exists():	
					fileOut.delete()

			return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())	

Gimp.main(PythonRemoveBG.__gtype__, sys.argv)
