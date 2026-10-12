#!/usr/bin/env python3
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
import sys
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

class PythonInstagram1977(Gimp.PlugIn):
		## GimpPlugIn virtual methods ##
		def do_set_i18n(self, procname):
			return True, 'gimp30-python', None

		def do_query_procedures(self):
			return [ 'Instagram1977' ]

		def do_create_procedure(self, name):
			procedure = Gimp.ImageProcedure.new(self, name,
										Gimp.PDBProcType.PLUGIN,
										self.instagram1977, None)
			procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)
			procedure.set_image_types("RGB*")
			procedure.set_documentation ("Instagram1977",
										"Instagram1977",
										 name)
			procedure.set_attribution("M",
										"(c) GPL V3.0 or later",
										"2026")
			procedure.set_menu_label("Instagram1977")
			procedure.add_menu_path('<Image>/Filters/')
			
			return procedure

		def instagram1977(self, procedure, run_mode, img,  drawables, config, run_data ):

			Gimp.context_pop()
			img.undo_group_start()
			
			lg = Gimp.GroupLayer.new(img)
			lg.set_name("1977 Effect")
			img.insert_layer(lg,None,-1)

			drawCopy = Gimp.Layer.new_from_drawable(drawables[0],img)
			img.insert_layer(drawCopy,lg,0)
			#adjust curves colors
			drawCopy.curves_spline(Gimp.HistogramChannel.ALPHA,(0,60, 65,70, 255,255) )
			Gimp.Selection.all(img)
		
			sel_size = Gimp.Selection.bounds(img)
			w = sel_size.x2 -  sel_size.x1
			h = sel_size.y2 -  sel_size.y1

			l =  Gimp.Layer.new(img,"1977Col",w,h,Gimp.ImageType.RGBA_IMAGE,100.0,Gimp.LayerMode.DARKEN_ONLY)
			img.insert_layer(l, lg,0)
			color = Gegl.Color.new("rgba(227,255,215,0)")
			Gimp.context_set_foreground(color)
			l.edit_fill(Gimp.FillType.FOREGROUND)
			l.set_mode(Gimp.LayerMode.DARKEN_ONLY)

			Gimp.Selection.none(img)
			#add white border
			Wborder = Gimp.Layer.new(img,"whiteBorder",w,h,Gimp.ImageType.RGBA_IMAGE,100.0,Gimp.LayerMode.NORMAL)
			img.insert_layer(Wborder, lg, 0)
			wcolor = Gegl.Color.new("white")
			Gimp.context_set_foreground(wcolor)
			img.select_rectangle(0, 0,0, w,h )
			dimBorder = int( (w/100)*2 )
			dimBorder = max(dimBorder,5)
			Gimp.Selection.shrink(img, dimBorder)
			Gimp.Selection.invert(img)
			Wborder.edit_fill(Gimp.FillType.FOREGROUND)
			Gimp.Selection.none(img)
	
			#add black border
			Bborder = Gimp.Layer.new(img,"blackBorder",w,h,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
			img.insert_layer(Bborder,lg , 0)
			bcolor = Gegl.Color.new("#000000")
			Gimp.context_set_foreground(bcolor)
			img.select_rectangle( 0, 0,0, w,h )
		
			dimBorder = int( (w/100)*2 )
			dimBorder = max(dimBorder,5)
			Gimp.Selection.shrink(img, dimBorder)
			Gimp.Selection.invert(img)
			Bborder.edit_fill(Gimp.FillType.FOREGROUND)
			Gimp.Selection.none(img)

			img.undo_group_end()
			Gimp.displays_flush()

			return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

Gimp.main(PythonInstagram1977.__gtype__, sys.argv)
