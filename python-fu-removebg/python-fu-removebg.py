#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import os, sys, string, tempfile, platform

def N_(message): return message
def _(message): return GLib.dgettext(None, message)
tupleModel = ("u2net","u2net_human_seg", "u2net_cloth_seg", "u2netp", "silueta", "isnet-general-use", "isnet-anime", "sam", "birefnet-general" ,"birefnet-general-lite", "birefnet-portrait", "birefnet-dis", "birefnet-hrsod", "birefnet-cod", "birefnet-massive" )

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
			procedure.set_menu_label(_("RemoveBG.."))
			procedure.set_attribution("Joao S. O. Bueno",
										"(c) GPL V3.0 or later",
										"2011")
			procedure.add_menu_path('<Image>/Filters/RemoveBG/')

			procedure.add_boolean_argument("asMask","as Mask","As mask",False,GObject.ParamFlags.READWRITE)
			procedure.add_boolean_argument("AlphaMatting","AlphaMatting","AlphaMatting",False,GObject.ParamFlags.READWRITE)
			procedure.add_double_argument("aeValue","aeValue","aeValue",0,100,15 ,GObject.ParamFlags.READWRITE)


			pchannel_choice = Gimp.Choice.new()
			pchannel_choice.add("u2net",0,"u2net","")
			pchannel_choice.add("u2net_human_seg",1,"u2net_human_seg","")
			pchannel_choice.add("u2net_cloth_seg",2,"u2net_cloth_seg","")
			pchannel_choice.add("u2netp",3,"u2netp","")
			pchannel_choice.add("silueta",4,"silueta","")
			pchannel_choice.add("isnet-general-use",5,"isnet-general-use","")
			pchannel_choice.add("isnet-anime",6,"isnet-anime","")
			pchannel_choice.add("sam",7,"sam","")
			pchannel_choice.add("birefnet-general",8,"birefnet-general","")
			pchannel_choice.add("birefnet-cod",9,"birefnet-cod","")
			pchannel_choice.add("birefnet-massive",10,"birefnet-massive","")
			pchannel_choice.add("birefnet-portrait",11,"birefnet-portrait","")
			pchannel_choice.add("birefnet-general-lite",12,"birefnet-general-lite","")
			pchannel_choice.add("birefnet-hrsod",13,"birefnet-hrsod","")
			pchannel_choice.add("birefnet-dis",14,"birefnet-dis","")

			procedure.add_choice_argument ("Model", _("Model"),
                                           _("Model"), pchannel_choice,
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

			removeTmpFile = True
			osName = platform.system()

			exportSep = str(os.sep)
			tdir = tempfile.gettempdir()
			print(tdir)
			jpgFile = "%s%sTemp-gimp-0000.jpg" % (tdir, exportSep)
			pngFile = "%s%sTemp-gimp-0000.png" % (tdir, exportSep)
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
	
			aiExe = "C:\\Program Files (x86)\\Rembg\\rembg.exe"
			
			if AlphaMatting:
				option = "-a -ae %d" % (aeValue)
			cmd = '""%s" i -m %s %s "%s" "%s""' % (aiExe, tupleModel[selModel], option, f.get_path(), pngFile)
			os.system(cmd)

			file_exists = os.path.exists(pngFile)
			if file_exists:
				newlayer = Gimp.file_load_layer(run_mode,image,fileOut)
				image.insert_layer(newlayer, None,-1)
			
			file = Gio.File.new_for_path(pngFile)
			newLayer  = Gimp.file_load_layer(run_mode,image,fileOut)
			image.insert_layer(newlayer, None,-1)

			if asMask:
				pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, newlayer)
				image.remove_layer(newlayer)
				copyLayer = pdb.gimp_layer_copy(curLayer, TRUE)
				image.add_layer(copyLayer, -1)
				mask=copyLayer.create_mask(ADD_SELECTION_MASK)
				copyLayer.add_mask(mask)
				pdb.gimp_selection_none(image)

			image.undo_group_end()
			Gimp.displays_flush()

			if removeTmpFile:
				if file.query_exists():
					file.delete()
				if fileOut.query_exists():	
					fileOut.delete()

			return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())	

Gimp.main(PythonRemoveBG.__gtype__, sys.argv)
