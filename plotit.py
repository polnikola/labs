""" Plotit module
Модуль содержит отдельные функции для быстрой интеграции в произвольный код через 
- копирование модуля в папку проекта или 
- текста функции в текст пользовательской программы.

"""

# общие библиотеки
from typing import Iterable
import numpy as np
# библиотеки для plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import qualitative
# библиотеки для matplotlib
import matplotlib
from matplotlib import pyplot as plt

from matplotlib.animation import FuncAnimation  # библиотека для анимации
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.container import BarContainer
from matplotlib.collections import PathCollection


# Вывод графиков с использованием plotly
def plotit_plotly(
		y, x=None,
		names=None,
		lines=None, widths=None, colors=None, opacities=None,
		x_label=None, y_label=None,
		x_scale="linear", y_scale="linear",
		x_lims: list = None,    y_lims: list = None,
		title: str = None, 
		ax=None, row_col=[None, None],
		error_x=None, error_y=None, error_thickness=1.0,
		mode='lines',
		renderer=None,
		file_name=None,
		):
	"""
	Plot data using plotly.
	Args:
		y (ndarray): y axis.
		x (ndarray, optional): x axis values, if None - automatic x axis generation.
		title (str, optional): Title of the plot (sets title only for the figure initiation).
		legend (list, optional): List of curve titles, if False is supplied, then legend item is hidden.
		x_label (str, optional): Label for the X axis.
		y_label (str, optional): Label for the Y axis.
		x_lims (list, optional): Limits of the range for the X axis.
		y_lims (list, optional): Limits of the range for the Y axis.
		x_scale (str, optional): Scale of the x-axis. Defaults to "linear".
		y_scale (str, optional): Scale of the y-axis. Defaults to "linear". Valid values: "linear", "log".
		error_x (ndarray, optional): Offset for the error whiskers.
		error_y (ndarray, optional): Offset for the error whiskers.
		error_thickness (float): Thickness of the error whiskers.
		dashes (str, optional): List of line types. Valid values: 'solid' (=None), 'dash', 'dot', 'dashdot'.
		widths (optional): List of line widths, or a single value.
		opacity (Iterable, optional): List or value of opacity, transferred to the go.Scatter.
		colors (optional): List of color names/values redirected to the go.Scatter object. Int values are supported.
		renderer (optional): Defines how to render the plot.
		ax (optional): Returning ax for future use or modifying existing.
		row_col (list, optional): If subplots are used, select row and column.
		file_name (str, optional): Name of the file to export the plot image.
	Returns:
		plotly.graph_objects.Scatter: Returns Figure object, that can be altered.

	Example 1. Plot single ndarray:
		>>> import numpy as np
		>>> from plotit import plotit_plotly as plot
		>>> y = np.arange(10)**2
		>>> plot(y)

	Example 2. Plot list:
		>>> import numpy as np
		>>> from plotit import plotit_plotly as plot
		>>> y = [np.arange(10)**2, np.arange(10)]
		>>> plot(y, names=['quad', 'lin'])

	"""
	# Handle 1D input by expanding to 2D
	if isinstance(y, np.ndarray) and y.ndim == 1:
		y = y[:, np.newaxis]

	# Handle list/tuple inputs by combining into ndarray
	if isinstance(y, (list, tuple)):
		if y[0].ndim == 1:
			y = np.stack(y, axis=1)
		else:
			y = np.concatenate(y, axis=1)

	if isinstance(error_y, bool) and error_y:
		error_y = np.concatenate([np.std(arr, axis=1, keepdims=True) for arr in y], axis=1)
		y = np.concatenate([np.mean(arr, axis=1, keepdims=True) for arr in y], axis=1)

	if np.any(np.iscomplex(y)):
		print("Warning: Complex data supplied - ignoring imaginary parts")
		y = np.real(y)

	n_plot_lines = min(y.shape[1], 10)  # Limit to 10 lines for clarity
	
	# If colors are integers, select by order 
	if colors is not None:
		if isinstance(colors, (int, str)):  colors = [colors] * n_plot_lines
		if isinstance(colors, list):        colors = [qualitative.D3[c] if isinstance(c, int) else c for c in colors]

	if names is None:
		names = [None] * n_plot_lines
	line_properties = [{'dash': lines[i] if lines else None,
						'width': widths[i] if widths else None,
						'color': colors[i] if colors else None}
					   for i in range(n_plot_lines)]
	if x is None:
		x = np.arange(y.shape[0])
	plots = [
		go.Scatter(
			x=x, y=y[:, i], mode=mode, name=names[i],
			line=line_properties[i],
			opacity=opacities[i] if opacities else None,
			error_x=dict(type='data', array=error_x[:, i], visible=True, thickness=error_thickness) if isinstance(error_x, np.ndarray) else None,
			error_y=dict(type='data', array=error_y[:, i], visible=True, thickness=error_thickness) if isinstance(error_y, np.ndarray) else None
		)
		for i in range(n_plot_lines)
	]
	if ax is None:
		fig = go.Figure(layout=go.Layout(showlegend=True, title=title))
	elif isinstance(ax, list):
		if len(ax)==0:
			ax.append(go.Figure(layout=go.Layout(title=title)))
		elif ax[-1] is None:
			ax[-1] = go.Figure(layout=go.Layout(title=title))
		elif isinstance(ax[-1], int):
			f = ax[-1]
			f = (f,1) if f<10 else divmod(f, 10)
			ax[-1] = make_subplots(*f, shared_xaxes='columns')
		fig = ax[-1]
	else:
		fig = ax

	if isinstance(row_col, int):
		if row_col<=10:
			row_col = (row_col, 1)
		else:		   row_col = divmod(row_col, 10)
	for p in plots:
		fig.add_trace(p, row=row_col[0], col=row_col[1])
	fig.update_layout(template='none')
	fig.update_xaxes(title_text=x_label, range=x_lims, type=x_scale, tickformat='s')
	fig.update_yaxes(title_text=y_label, range=y_lims, type=y_scale, tickformat='s')
	if renderer is None:
		if ax is None:
			fig.show()
	elif renderer:
		if isinstance(renderer, str):
			fig.show(renderer=renderer)
		elif renderer is True:
			fig.show(renderer='browser')
	if file_name:
		fig.write_image(file_name)
	if ax is not None:
		return None  # If figure is modified in place
	# return fig


# Вывод графиков с использованием matplotlib
def plotit_pyplot(
		y, x=None,
		names=None,
		lines=None, widths=None, colors=None, opacities=None,
		x_label=None,   y_label=None,
		x_scale='linear',   y_scale='linear',
		x_lims: list = None, y_lims: list = None,
		title: str = None,  
		ax=None,
		grid=True,
		):
	"""Рисование графиков

	Args:
		y (_type_): ординаты
		x (_type_, optional): абсциссы. Defaults to None.
		names (list, optional): имена кривых для легенды. Defaults to None.
		lines (list, optional): типы линий. Defaults to None.
		widths (list, optional): толщины линий. Defaults to None.
		colors (list, optional): цвета линий (целые значения - порядковые номера). Defaults to None.
		opacities (list, optional): прозрачности. Defaults to None.
		y_scale (str, optional): тип оси (линейная, логарифм и проч.). Defaults to None.
		y_lims (list, optional): границы по ординатам. Defaults to None.
		x_lims (list, optional): границы по абсциссам. Defaults to None.
		y_label (str, optional): название оси ординат. Defaults to None.
		x_label (str, optional): название оси абсцисс. Defaults to None.
		title (str, optional): заголовок графика. Defaults to None.
		grid (bool, optional): рисовать сетку. Defaults to True.
		ax (_type_, optional): ось на которую добаляется график. Defaults to None.

	Returns:
		_type_: _description_


	Example 1. Plot single ndarray:
		>>> import numpy as np
		>>> from plotit import plotit_pyplot as plot
		>>> y = np.arange(10)**2
		>>> plot(y)

	Example 2. Plot list:
		>>> import numpy as np
		>>> from plotit import plotit_pyplot as plot
		>>> y = [np.arange(10)**2, np.arange(10)]
		>>> plot(y, names=['quad', 'lin'])
	"""
	if not isinstance(y,(list,tuple)): 
		y = [y]
		if isinstance(names,str): names = [names]
	if names is None:       names=[None]*len(y)
	if lines is None:       lines = ['solid'] * len(y)
	if widths is None:      widths = [1.5] * len(y)
	if opacities is None:	opacities = [1.0] * len(y)
	
	if colors is None:
		colors = [None] * len(y)
	prop_cycle = plt.rcParams['axes.prop_cycle']
	color_cycle = prop_cycle.by_key()['color']
	
	if not isinstance(x,(list,tuple)):
		if x is None:   x = [np.arange(_.shape[-1]) for _ in y]
		else:		   x = [x]*len(y)
	# if ax is None:		figure, ax = plt.subplots()
	# else: figure = None
	figure ,ax = _plt_ax_parser(ax)
	for i in range(len(y)):
		color = color_cycle[colors[i] % len(color_cycle)] if colors[i] is not None else None
		ax.plot(x[i], y[i], label=names[i], color=color,
				linestyle=lines[i], linewidth=widths[i], alpha=opacities[i])
	# if names[0] is not None: ax.legend()
	if names[0] is not None:
		# ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
		ax.legend(loc='upper right', framealpha=0.5)  # framealpha sets transparency (0 = fully transparent, 1 = fully opaque)
		enable_interactive_legend(ax)
	ax.set_xlabel(x_label)
	ax.set_ylabel(y_label)
	ax.set_xlim(x_lims)
	ax.set_ylim(y_lims)
	ax.set_title(title)
	ax.set_xscale(x_scale)
	ax.set_yscale(y_scale)
	ax.grid(grid)
	# if matplotlib.get_backend() == "Qt5Agg":
	if 'Qt'.lower() in matplotlib.get_backend().lower():
		ax.figure.canvas.manager.window.raise_()  # Only runs if Qt5Agg is used
	ax.figure.tight_layout()
	enable_click_crosshair(ax)
	# if figure is not None: 	return figure, ax


# Анимация
def run_animation(y, x=None, save_file=None, x_label='x', y_label='y', titles=None, ax=None, fps=12):
	"""_summary_

	Args:
		y (_type_): _description_
		x (_type_, optional): _description_. Defaults to None.
		save_file (_type_, optional): _description_. Defaults to None.
		x_label (str, optional): _description_. Defaults to 'x'.
		y_label (str, optional): _description_. Defaults to 'y'.
		titles (_type_, optional): _description_. Defaults to None.

	Returns:
		_type_: _description_

	Example 1. Animate list of single plots
		>>> import numpy as np
		>>> import matplotlib
		>>> matplotlib.use('Qt5Agg')
		>>> from matplotlib import pyplot as plt
		>>> plt.ion()
		>>> from plotit import run_animation as animate
		>>> t = np.linspace(0,1,100)
		>>> phis = np.linspace(0,2*np.pi,10)
		>>> y = [np.sin(10*t+phi) for phi in phis]
		>>> animate(y, t, titles=[f'φ={phi:0.1f} rad' for phi in phis])

	"""
	
	# Check if the current backend is non-interactive and switch if needed
	if matplotlib.get_backend() not in ['Qt4Agg', 'Qt5Agg', 'TkAgg']: raise RuntimeError(f"Only 'Qt4Agg', 'Qt5Agg', 'TkAgg' are supported, but {matplotlib.get_backend()} is used. Try running matplotlib.use('Qt5Agg').")
	if isinstance(y, (list, tuple)): 
		y = np.stack(y, axis=0)
		
	# fig, ax = plt.subplots()
	fig, ax = _plt_ax_parser(ax)
		
	ax.set(xlabel=x_label, ylabel=y_label, xlim=(np.min(x), np.max(x)), ylim=(1.1 * np.min(y), 1.1 * np.max(y)))
	lines = []
	if x is None: x = np.arange(y[0].shape[-1])

	if y.ndim == 3:  # If y is a 3D array, create multiple lines
		for i in range(y.shape[0]):
			line, = ax.plot([], [], lw=1.5)
			lines.append(line)
	else:  # If y is a 2D array, create a single line
		line, = ax.plot([], [], lw=1.5)
		lines.append(line)

	def init():
		for line in lines:
			line.set_data([], [])
		return lines

	def animate(i):
		# Update each line's data based on the frame index i
		if y.ndim == 3:  # Animate multiple lines
			for j, line in enumerate(lines):
				line.set_data(x, y[j, i, :])
		else:  # Animate a single line
			lines[0].set_data(x, y[i, :])
		
		# Set the title for the current frame, if titles are provided
		if titles is not None and i < len(titles):
			ax.set_title(titles[i])
		return lines

	blit = titles is None   # if no titles than redraw only lines
	anim = FuncAnimation(fig, animate, init_func=init, frames=y.shape[-2], interval=1/fps, blit=blit, repeat=True, repeat_delay=1/fps)
	if save_file is not None:
		anim.save(save_file, writer='PillowWriter', dpi=96, fps=fps, bitrate=256)

	plt.show()
	return anim


# Отображение созвездия
def plot_constellation(complex_values, names=None, ax=None):
	"""
	Plots a constellation diagram from an array of complex values.
	Parameters:
		complex_values (array-like): An array of complex numbers representing the signal points.
	"""
	# Extract real and imaginary parts
	real_parts = np.real(complex_values)
	imaginary_parts = np.imag(complex_values)

	# Create a scatter plot using matplotlib
	# if ax is None:
	# 	_, ax = plt.subplots()
	_, ax = _plt_ax_parser(ax)


	scatter = ax.scatter(real_parts, imaginary_parts, s=8, label=names, alpha=0.75)

	# Optional: label points with complex values
	# for i, val in enumerate(complex_values):
		# ax.text(real_parts[i], imaginary_parts[i], f'{val:.2f}', fontsize=10)

	# Add axis labels and title
	ax.set_title('Созвездие')
	ax.set_xlabel('Действ.')
	ax.set_ylabel('Мним.')
	ax.grid(True)

	lim = 1.1*np.max(np.abs(complex_values))
	ax.set_xlim([-lim, lim])
	ax.set_ylim([-lim, lim])

	if names is not None:
		ax.legend()

	plt.gca().set_aspect('equal', adjustable='box')
	
	if names is not None:
		ax.legend(loc='upper right', bbox_to_anchor=(1, 1))

	# ax.figure.tight_layout()
	# ax.figure.canvas.manager.window.raise_()
	if ax is None:
		plt.show()
	elif isinstance(ax, list):
		if len(ax) == 0:
			ax.append(ax)
		else:
			ax[-1] = ax



def enable_interactive_legend(ax=None):
	"""
	Make legend labels clickable to toggle visibility of the corresponding artist(s).

	This function enhances a Matplotlib legend to be interactive: clicking a legend
	label will show or hide the corresponding plot element(s) (such as lines,
	patches, bars, or scatter points) in the associated Axes.

	Parameters
	----------
	ax : matplotlib.axes.Axes, optional
		The target Axes containing the legend. If None, uses the current axes (plt.gca()).

	Raises
	------
	RuntimeError
		If no legend is found on the given Axes.

	Supported Artist Types
	----------------------
	- Line2D: Standard line plots.
	- Patch: Single patch elements (excluding Rectangle).
	- BarContainer: Groups of rectangles (bars) from ax.bar().
	- PathCollection: Scatter plots (plt.scatter()).
	- Rectangle: Histogram bars or similar rectangular patches.

	Notes
	-----
	- The function maps each legend text entry to one or more artists in the plot.
	- When a legend label is clicked, its corresponding artists are toggled between
	  visible/hidden, and the legend label fades to indicate the hidden state.
	- This works well for mixed plots (lines, bars, scatter, etc.) that share a legend.

	Example
	-------
	>>> import matplotlib.pyplot as plt
	>>> import numpy as np
	>>> x = np.linspace(0, 10, 100)
	>>> y1 = np.sin(x)
	>>> y2 = np.cos(x)
	>>> plt.plot(x, y1, label='sin(x)')
	>>> plt.plot(x, y2, label='cos(x)')
	>>> plt.legend()
	>>> enable_interactive_legend()  # make legend clickable
	>>> plt.show()
	"""

	if ax is None:
		ax = plt.gca()  # Use current axes if none provided
	fig = ax.figure
	# ax.legend()  # (Optional) Could regenerate legend if needed
	leg = ax.get_legend()
	if leg is None:
		raise RuntimeError("No legend found on this axis.")

	# Retrieve handles and labels associated with the legend
	handles, labels = ax.get_legend_handles_labels()

	# Build mapping from legend text object → corresponding plot artist(s)
	legend_map = {}
	for text, handle in zip(leg.get_texts(), handles):
		artists = []

		if isinstance(handle, Line2D):
			# Simple line plots
			artists.append(handle)

		elif isinstance(handle, Patch) and not isinstance(handle, Rectangle):
			# Single patch (like a filled polygon or area)
			artists.append(handle)

		elif isinstance(handle, BarContainer):
			# For bar charts: expand BarContainer into individual bar rectangles
			artists.extend(handle.patches)

		elif isinstance(handle, PathCollection):
			# For scatter plots
			artists.append(handle)

		elif isinstance(handle, Rectangle):
			# Handle histogram-like cases where legend contains one Rectangle
			face = handle.get_facecolor()
			edge = handle.get_edgecolor()
			# Find all rectangles on the same Axes matching the same color and edge
			matching = [
				p for p in ax.patches
				if isinstance(p, Rectangle)
				and (p.get_facecolor() == face)
				and (p.get_edgecolor() == edge)
			]
			if matching:
				# Use all matching bars as linked artists
				artists.extend(matching)
			else:
				# Fallback: just use the legend's rectangle
				artists.append(handle)

		# Register mapping and enable click detection for this legend text
		legend_map[text] = artists
		text.set_picker(True)


	def on_pick(event):
		"""Callback function to handle legend text click events."""
		text = event.artist
		if text not in legend_map:
			return

		# Toggle visibility state
		visible = not legend_map[text][0].get_visible()
		for art in legend_map[text]:
			art.set_visible(visible)

		# Dim legend text if the corresponding plot elements are hidden
		text.set_alpha(1.0 if visible else 0.2)

		# Redraw canvas to reflect changes
		fig.canvas.draw_idle()

	# Connect the callback to the pick event
	fig.canvas.mpl_connect("pick_event", on_pick)



def enable_click_crosshair(ax=None, opacity=0.25, cross_size=5, tolerance=0.005): 
	"""
	Enable interactive click-based crosshair annotations on a Matplotlib Axes.

	When you left-click near a data point, a small black “×” crosshair and
	a coordinate text box will appear at that location. The text box background
	automatically matches the color of the data object under the cursor
	(line or scatter point), or grey if none is detected.

	Clicking an existing annotation (either its text or crosshair marker)
	removes both. After a removal, the *next* click is ignored to prevent
	immediate re-creation at the same spot.

	This function supports both:
		• Line2D objects (standard `plot`)
		• PathCollection objects (`scatter` plots)

	Parameters
	----------
	ax : matplotlib.axes.Axes, optional
		Target axes for interactivity. Defaults to current axes (`plt.gca()`).
	opacity : float, default=0.25
		Transparency level of the annotation background box (0–1).
	cross_size : int, default=5
		Size of the “×” crosshair marker in points.
	tolerance : float, default=0.005
		Proximity tolerance in y-data units (as a fraction of axis y-range)
		to detect nearby points.

	Returns
	-------
	cid_button : int
		Connection ID for the `button_press_event` callback.
	cid_pick : int
		Connection ID for the `pick_event` callback.
	markers : list of matplotlib.lines.Line2D
		Currently drawn crosshair markers.
	annotations : list of matplotlib.text.Text
		Currently drawn coordinate text annotations.

	Example
	-------
	>>> import matplotlib.pyplot as plt
	>>> import numpy as np
	>>> x = np.linspace(0, 2*np.pi, 100)
	>>> y = np.sin(x)
	>>> plt.plot(x, y, label='sin(x)')
	>>> plt.scatter(x, y, color='red', label='points')
	>>> plt.legend()
	>>> enable_click_crosshair()  # Click near line or scatter points
	>>> plt.show()
	"""
	if ax is None:
		ax = plt.gca()  # Use the active axes if not provided
	fig = ax.figure

	# Track all active crosshair markers and annotation texts
	markers = []
	annotations = []

	# Maintain mappings for quick removal of paired objects
	text_to_marker = {}
	marker_to_text = {}

	# Suppress flag to avoid adding a new annotation immediately after deletion
	suppress_next_click = {'val': False}

	def onclick(event):
		"""Handle mouse clicks: create new crosshair/text annotations."""
		# Ignore click if it immediately follows a removal
		if suppress_next_click['val']:
			suppress_next_click['val'] = False
			return

		# Ignore clicks outside of this axes
		if event.inaxes != ax:
			return

		# Only respond to left-click (button=1)
		if event.button != 1:
			return

		# Get click coordinates (in data space)
		x_click, y_click = event.xdata, event.ydata
		if x_click is None or y_click is None:
			return

		# Default text box background color
		bg_color = 'grey'

		# Convert tolerance fraction to absolute y-units
		tol = tolerance * (ax.get_ylim()[1] - ax.get_ylim()[0])

		# --- Handle Line2D objects (standard plots) ---
		for line in ax.get_lines():
			xdata, ydata = line.get_xdata(), line.get_ydata()
			if len(xdata) == 0:
				continue

			# Find nearest x-coordinate index
			idx = np.argmin(np.abs(xdata - x_click))

			# If vertical distance within tolerance, mark as selected
			if np.abs(ydata[idx] - y_click) <= tol:
				# Snap click location to nearest point
				y_click, x_click = ydata[idx], xdata[idx]
				bg_color = line.get_color()

				# Draw small black crosshair marker
				marker, = ax.plot(
					x_click, y_click,
					marker='x', color='black',
					markersize=cross_size,
					markeredgewidth=1.5,
					linestyle='None'
				)
				marker.set_picker(True)  # Make selectable for removal

				# Add coordinate label next to crosshair
				txt = ax.text(
					x_click, y_click,
					f"({x_click:.3f}, {y_click:.3f})",
					fontsize=9,
					ha='left', va='bottom',
					bbox=dict(boxstyle="round,pad=0.3", fc=bg_color, alpha=opacity)
				)
				txt.set_picker(True)

				# Store references for cleanup
				markers.append(marker)
				annotations.append(txt)
				text_to_marker[txt] = marker
				marker_to_text[marker] = txt

				fig.canvas.draw_idle()
				break  # Stop after handling first matching line point

		# --- Handle PathCollection objects (scatter plots) ---
		for coll in ax.collections:
			# Only process scatter-like collections
			if not hasattr(coll, 'get_offsets'):
				continue
			offsets = np.asarray(coll.get_offsets())
			if offsets.size == 0:
				continue

			# Compute distances between click and each scatter point
			dists = np.hypot(offsets[:, 0] - x_click, offsets[:, 1] - y_click)
			idx = int(np.argmin(dists))

			# Check if nearest point is within tolerance
			if dists[idx] <= tol:
				# Determine background color (prefer facecolor)
				try:
					fc = coll.get_facecolors()
					if fc is None or len(fc) == 0:
						raise Exception
					color = tuple(fc[0])
				except Exception:
					try:
						ec = coll.get_edgecolors()
						color = tuple(ec[0]) if len(ec) > 0 else 'grey'
					except Exception:
						color = 'grey'
				bg_color = color

				# Draw crosshair at selected scatter point
				x_pt, y_pt = offsets[idx, 0], offsets[idx, 1]
				marker, = ax.plot(
					x_pt, y_pt, marker='x', color='black',
					markersize=cross_size, markeredgewidth=1.5, linestyle='None'
				)
				marker.set_picker(True)

				# Draw coordinate label
				txt = ax.text(
					x_pt, y_pt,
					f"({x_pt:.3f}, {y_pt:.3f})",
					fontsize=9,
					ha='left', va='bottom',
					bbox=dict(boxstyle="round,pad=0.3", fc=bg_color, alpha=opacity)
				)
				txt.set_picker(True)

				# Track objects for removal
				markers.append(marker)
				annotations.append(txt)
				text_to_marker[txt] = marker
				marker_to_text[marker] = txt

				fig.canvas.draw_idle()
				return  # Stop after first matching scatter point

		# If no match found (click not near any data), do nothing
		return

	def onpick(event):
		"""Handle pick events to remove annotations and linked markers."""
		art = event.artist  # Picked artist (Text or Line2D)
		removed_any = False

		# Case 1: user clicked text label
		if art in text_to_marker:
			marker = text_to_marker.pop(art)
			marker_to_text.pop(marker, None)

			# Remove both safely
			for obj in (art, marker):
				try:
					obj.remove()
				except Exception:
					pass

			# Update lists
			if art in annotations:
				annotations.remove(art)
			if marker in markers:
				markers.remove(marker)

			removed_any = True

		# Case 2: user clicked crosshair marker
		elif art in marker_to_text:
			txt = marker_to_text.pop(art)
			text_to_marker.pop(txt, None)

			# Remove both safely
			for obj in (art, txt):
				try:
					obj.remove()
				except Exception:
					pass

			# Update lists
			if art in markers:
				markers.remove(art)
			if txt in annotations:
				annotations.remove(txt)

			removed_any = True

		# After deletion, suppress the next click
		if removed_any:
			suppress_next_click['val'] = True
			fig.canvas.draw_idle()

	# Register callbacks with the figure event system
	cid_button = fig.canvas.mpl_connect('button_press_event', onclick)
	cid_pick = fig.canvas.mpl_connect('pick_event', onpick)

	# Return callback IDs and current object lists
	return cid_button, cid_pick, markers, annotations

def _plt_ax_parser(ax):
	"""
	Normalize various matplotlib axis/figure specifications into a (fig, ax) pair.

	This small utility accepts multiple forms of matplotlib handles and returns a
	consistent `(Figure, Axes)` tuple. It is intended to simplify interface code
	that wants to support flexible `ax` arguments.

	Parameters
	----------
	ax : None | matplotlib.figure.Figure | matplotlib.axes.Axes | str | numpy.ndarray
		- None:
			Creates a new figure and axis using `plt.subplots(1,1)`.
		- Figure:
			Uses the existing figure. If it has axes, returns the last one;
			otherwise creates a new axis.
		- Axes:
			Uses the supplied axis and retrieves its parent figure.
		- str:
			Treated as a figure name/ID. A figure with that name is created/
			selected, and a new axis (`111`) is added.
		- numpy.ndarray of Axes:
			Flattens the array and uses the last axis in it, along with its figure.

	Returns
	-------
	fig : matplotlib.figure.Figure
		The resolved or created figure instance.
	ax : matplotlib.axes.Axes
		The resolved or created axis instance. An attribute `ax.show` is also set
		to point to the parent figure's `show` method for convenience.

	Raises
	------
	TypeError
		If `ax` is none of the supported types.

	Notes
	-----
	- When a Figure is passed, a new axis is only created if the figure has no axes.
	- When a string is passed, it acts as a Figure identifier for `plt.figure(name)`.
	- Overloads the axis with `ax.show = fig.show` to mimic figure-level showing.
	"""
	# Figure instance: add axis
	if isinstance(ax, plt.Figure):  
		fig = ax
		# ax = fig.add_subplot(111)
		ax = ax.axes[-1] if len(ax.axes) else ax.add_axes(111)
	# Figure name = string ID: select, get handle & add axis
	elif isinstance(ax,str):        
		fig = plt.figure(ax)
		if fig.axes:    ax = fig.axes.flat[-1]
		else:           ax = fig.add_subplot(111)
	# Axis handle: get figure handle
	elif isinstance(ax, plt.Axes):  
		fig = ax.figure
	# Axis array: get handles for the last axis and its figure
	elif isinstance(ax, np.ndarray):  
		ax = ax.flat[-1]
		fig = ax.figure
	# Create new figure and axis
	elif ax is None:                
		fig = plt.figure()
		ax = plt.subplot(111)
	# Raise error
	else:   
		raise TypeError('In pyplot mode ax can be a None, Figure or Axis')
	
	ax.show = fig.show
	return fig, ax