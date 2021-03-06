# abstract_classic_tool.py
#
# Copyright 2018-2020 Romain F. T.
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

import cairo
from .abstract_tool import AbstractAbstractTool
from .optionsbar_classic import OptionsBarClassic
from .utilities_blur import utilities_blur_surface

class AbstractClassicTool(AbstractAbstractTool):
	__gtype_name__ = 'AbstractClassicTool'

	def __init__(self, tool_id, label, icon_name, window, **kwargs):
		super().__init__(tool_id, label, icon_name, window)
		self.menu_id = 0
		self.use_color = True
		self.use_size = True
		self.accept_selection = False

		self.tool_width = 10
		self.main_color = None
		self.secondary_color = None
		self._fallback_operator = 'over'
		self._use_antialias = True
		self.x_press = 0.0
		self.y_press = 0.0
		self.add_tool_action_boolean('antialias', self._use_antialias)

	############################################################################
	# UI implementations #######################################################

	def try_build_pane(self):
		self.pane_id = 'classic'
		self.window.options_manager.try_add_bottom_pane(self.pane_id, self)

	def build_bottom_pane(self):
		return OptionsBarClassic(self.window)

	def on_tool_selected(self):
		# XXX shouldn't i update the label/menu/size/sensitivity/etc. here?
		pass

	############################################################################
	# Options ##################################################################

	def set_common_values(self, event_btn, event_x, event_y):
		self._use_antialias = self.get_option_value('antialias')
		self.tool_width = self.window.options_manager.get_tool_width()
		if event_btn == 1:
			self.main_color = self.window.options_manager.get_left_color()
			self.secondary_color = self.window.options_manager.get_right_color()
		if event_btn == 3:
			self.main_color = self.window.options_manager.get_right_color()
			self.secondary_color = self.window.options_manager.get_left_color()
		self.x_press = event_x
		self.y_press = event_y
		self._operator = self.window.options_manager.get_operator()[0]

	############################################################################
	# Operations common methods ################################################

	def start_tool_operation(self, operation):
		super().start_tool_operation(operation)
		context = self.get_context()
		if 'antialias' not in operation:
			antialias = cairo.Antialias.DEFAULT
			# print("pas de clef pour l'antialias :", operation['tool_id'])
		elif operation['antialias']:
			antialias = cairo.Antialias.DEFAULT
		else:
			antialias = cairo.Antialias.NONE
		context.set_antialias(antialias)
		return context

	def stroke_with_operator(self, operator, context, line_width, is_preview):
		context.set_operator(operator)
		is_blur = (operator == cairo.Operator.DEST_IN)
		if is_blur and is_preview:
			context.set_operator(cairo.Operator.CLEAR)

		if is_blur and not is_preview:
			context.set_line_width(line_width)
			context.stroke_preserve()
			radius = int(line_width / 2)
			source_surface = self.get_surface()
			# XXX using the whole surface is suboptimal
			blurred_surface = utilities_blur_surface(source_surface, radius, 3, 0)
			# where 0 == BlurType.CAIRO_REPAINTS and 0 == BlurDirection.BOTH
			self.restore_pixbuf()
			context = self.get_context()
			context.set_operator(cairo.Operator.OVER)
			context.set_source_surface(blurred_surface, 0, 0)
			context.paint()
		else:
			context.set_line_width(line_width)
			context.stroke()

	############################################################################
################################################################################
