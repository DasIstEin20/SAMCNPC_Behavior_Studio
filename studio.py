"""SAMCNPC Behavior Studio. Python 3.10+ / standard-library Tkinter only."""
from __future__ import annotations
import copy
import math
import sys
import traceback
from weakref import WeakKeyDictionary
from diagnostics import log_exception
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
from engine import (Graph, Node, StudioError, CATALOG, CONDITIONS, ACTIONS, CHANNELS,
                    BUILTINS, strict_json, dump, validate_pack, require_export, export_zip,
                    atomic_write, safe_filename, check_install, install, installation_text, refresh_catalog)
from examples import EXAMPLES, load_example
from help_content import HELP
from i18n import DEFAULT_LANGUAGE, LANGUAGES, tr as ui_tr, example_label, localized_meta

BG='#111720'; PANEL='#19222e'; INPUT='#101924'; LINE='#2c3a4c'; FG='#e6edf6'; MUTED='#98adc2'
TEAL='#58d6bc'; BLUE='#78adff'; AMBER='#ffbe70'; RED='#ff858e'; PURPLE='#c6a1ff'
NODE_W=240; NODE_H=106
COLORS={'condition':TEAL,'all':TEAL,'any':TEAL,'not':TEAL,'rule':BLUE,'action':AMBER}


def display_meta(node, lang=DEFAULT_LANGUAGE):
    meta=(CONDITIONS if node.kind=='condition' else ACTIONS).get(node.ref,{})
    return localized_meta(lang, meta)

def node_title(node, lang=DEFAULT_LANGUAGE):
    if node.kind=='rule':return node.rule_id or ui_tr(lang,'new_rule_title')
    if node.kind in {'all','any','not'}:return {'all':ui_tr(lang,'logic_all'),'any':ui_tr(lang,'logic_any'),'not':ui_tr(lang,'logic_not')}[node.kind]
    return display_meta(node,lang).get('label',node.ref)

class GraphCanvas(tk.Canvas):
    def __init__(self,parent,app):
        super().__init__(parent,bg=BG,highlightthickness=0,takefocus=True)
        self.app=app;self.zoom=0.85;self.ox=25.;self.oy=35.
        self._font_cache = {}
        self._fit_cache = {}
        self.selected=None;self.selected_edge=None;self.pending=None;self.drag=None;self.pan=None;self.space=False;self.drag_before=None
        self.bind('<Configure>',lambda e:self.draw())
        self.bind('<Button-1>',self.down);self.bind('<B1-Motion>',self.motion);self.bind('<ButtonRelease-1>',self.up)
        self.bind('<Motion>',self.hover)
        self.bind('<Button-2>',self.pan_start);self.bind('<B2-Motion>',self.pan_move);self.bind('<ButtonRelease-2>',lambda e:setattr(self,'pan',None))
        self.bind('<Button-3>',self.context)
        self.bind('<MouseWheel>',self.wheel);self.bind('<Button-4>',lambda e:self.scale_at(e.x,e.y,1.12));self.bind('<Button-5>',lambda e:self.scale_at(e.x,e.y,1/1.12))
        self.bind('<KeyPress-space>',self.space_down);self.bind('<KeyRelease-space>',self.space_up)
        self.bind('<Escape>',lambda e:self.cancel_link());self.bind('<Delete>',lambda e:self.app.delete_selected())
        self.bind('<Key-f>',lambda e:self.fit());self.bind('<Key-F>',lambda e:self.fit())
    def space_down(self,e):self.space=True;self.configure(cursor='fleur');return 'break'
    def space_up(self,e):self.space=False;self.configure(cursor='');return 'break'
    def xy(self,x,y):return x*self.zoom+self.ox,y*self.zoom+self.oy
    def world(self,x,y):return (x-self.ox)/self.zoom,(y-self.oy)/self.zoom
    def port(self,nid,direction):
        n=self.app.graph.nodes[nid];return self.xy(n.x+(NODE_W if direction=='out' else 0),n.y+55)
    def port_hit(self,x,y):
        for nid,n in reversed(list(self.app.graph.nodes.items())):
            directions=[]
            if n.kind in {'rule','action','all','any','not'}:directions.append('in')
            if n.kind!='action':directions.append('out')
            for d in directions:
                px,py=self.port(nid,d)
                if math.hypot(px-x,py-y)<=max(10,9*self.zoom):return nid,d
        return None
    def node_hit(self,x,y):
        wx,wy=self.world(x,y)
        for nid,n in reversed(list(self.app.graph.nodes.items())):
            if n.x<=wx<=n.x+NODE_W and n.y<=wy<=n.y+NODE_H:return nid
        return None
    def edge_hit(self,x,y):
        for item in reversed(self.find_overlapping(x-6,y-6,x+6,y+6)):
            for t in self.gettags(item):
                if t.startswith('edge:'):
                    i=int(t.split(':')[1])
                    if i<len(self.app.graph.edges):return self.app.graph.edges[i]
        return None
    def down(self,e):
        self.focus_set()
        if self.space:self.pan_start(e);return
        hit=self.port_hit(e.x,e.y)
        if hit:
            nid,d=hit
            if d=='out':self.pending=nid;self.draw()
            elif self.pending:self.finish_link(nid)
            return
        nid=self.node_hit(e.x,e.y)
        if nid!=self.selected and self.app.inspector_pending() and not self.app.check_drafts():return
        self.selected=nid;self.selected_edge=None
        if nid:
            n=self.app.graph.nodes[nid];wx,wy=self.world(e.x,e.y)
            self.drag=(nid,wx-n.x,wy-n.y);self.drag_before=self.app.state()
        else:self.selected_edge=self.edge_hit(e.x,e.y)
        self.app.inspect();self.draw()
    def motion(self,e):
        if self.pan:self.pan_move(e);return
        if self.drag:
            nid,dx,dy=self.drag;n=self.app.graph.nodes.get(nid)
            if n:
                wx,wy=self.world(e.x,e.y);n.x=max(-1e5,min(1e5,wx-dx));n.y=max(-1e5,min(1e5,wy-dy));self.draw()
        elif self.pending:self.preview_line(e.x,e.y)
    def up(self,e):
        if self.pan:self.pan=None
        if self.drag:
            if self.drag_before!=self.app.state():self.app.record_before(self.drag_before);self.app.changed()
            self.drag=None;self.drag_before=None
        elif self.pending:
            hit=self.port_hit(e.x,e.y)
            if hit and hit[1]=='in':self.finish_link(hit[0])
    def hover(self,e):
        if self.pending:self.preview_line(e.x,e.y)
        elif not self.space:self.configure(cursor='crosshair' if self.port_hit(e.x,e.y) else '')
    def preview_line(self,x,y):
        self.delete('preview')
        if self.pending not in self.app.graph.nodes:return
        p=self.port(self.pending,'out');self.curve(*p,x,y,FG,tags='preview',dash=(5,4))
    def finish_link(self,nid):
        before=self.app.state()
        try:self.app.graph.connect(self.pending,nid)
        except StudioError as e:self.app.notify(str(e),error=True)
        else:self.app.record_before(before);self.app.changed();self.app.notify(self.app.tr('connected'))
        self.pending=None;self.draw()
    def cancel_link(self):self.pending=None;self.delete('preview');self.draw()
    def pan_start(self,e):self.pan=(e.x,e.y,self.ox,self.oy)
    def pan_move(self,e):
        if self.pan:
            x,y,ox,oy=self.pan;self.ox=ox+e.x-x;self.oy=oy+e.y-y;self.draw()
    def wheel(self,e):self.scale_at(e.x,e.y,1.12 if e.delta>0 else 1/1.12)
    def scale_at(self,x,y,factor):
        wx,wy=self.world(x,y);self.zoom=max(.18,min(2.0,self.zoom*factor));self.ox=x-wx*self.zoom;self.oy=y-wy*self.zoom;self.draw()
    def fit(self,ids=None):
        nodes=[n for k,n in self.app.graph.nodes.items() if ids is None or k in ids]
        if not nodes:return
        x0=min(n.x for n in nodes);y0=min(n.y for n in nodes)
        x1=max(n.x+NODE_W for n in nodes);y1=max(n.y+NODE_H for n in nodes)
        w=max(200,self.winfo_width());h=max(200,self.winfo_height())
        self.zoom=max(.18,min(1.1,(w-80)/max(1,x1-x0),(h-90)/max(1,y1-y0)))
        self.ox=(w-(x1-x0)*self.zoom)/2-x0*self.zoom;self.oy=(h-(y1-y0)*self.zoom)/2-y0*self.zoom
        self.draw()
    def context(self,e):
        self.focus_set();nid=self.node_hit(e.x,e.y);edge=None if nid else self.edge_hit(e.x,e.y)
        self.selected=nid;self.selected_edge=edge;self.app.inspect();self.draw()
        m=tk.Menu(self,tearoff=False,bg=PANEL,fg=FG,activebackground=LINE)
        if nid or edge:m.add_command(label=self.app.tr('ctx_delete_node') if nid else self.app.tr('ctx_delete_edge'),command=self.app.delete_selected)
        else:
            m.add_command(label=self.app.tr('ctx_add_rule'),command=lambda:self.app.add_node('rule',position=self.world(e.x,e.y)))
            for k,key in [('all','ctx_add_and'),('any','ctx_add_or'),('not','ctx_add_not')]:m.add_command(label=self.app.tr(key),command=lambda k=k:self.app.add_node(k,position=self.world(e.x,e.y)))
        m.tk_popup(e.x_root,e.y_root)
    def curve(self,x1,y1,x2,y2,color,**kw):
        dx=max(40,abs(x2-x1)*0.45)
        self.create_line(x1,y1,x1+dx,y1,x2-dx,y2,x2,y2,fill=color,width=max(1.4,2*self.zoom),smooth=True,splinesteps=32,arrow=tk.LAST,arrowshape=(8,10,4),**kw)
    def text_fit(self,text,length):return text if len(text)<=length else text[:length-1]+'…'
    def fitted(self, text, font_spec, width):
        """Bounded text fitting; keep Tk fonts alive across repaints.

        Creating/deleting a native font for every label and measuring one fewer
        character at a time made large translated graphs look frozen on X11.
        """
        key = (text, tuple(font_spec), max(0, math.floor(width)))
        cached = self._fit_cache.get(key)
        if cached is not None:
            return cached
        font = self._font_cache.get(key[1])
        if font is None:
            font = tkfont.Font(root=self, font=font_spec)
            self._font_cache[key[1]] = font
        available = key[2]
        if font.measure(text) <= available:
            result = text
        elif font.measure('…') > available:
            result = ''
        else:
            low, high = 0, len(text)
            while low < high:
                middle = (low + high + 1) // 2
                if font.measure(text[:middle] + '…') <= available:
                    low = middle
                else:
                    high = middle - 1
            result = text[:low] + '…'
        if len(self._fit_cache) >= 2048:
            self._fit_cache.clear()
        self._fit_cache[key] = result
        return result
    def draw(self):
        self.delete('all');w=self.winfo_width();h=self.winfo_height()
        spacing=max(16,32*self.zoom)
        for x in range(int(self.ox%spacing),max(1,w),max(1,int(spacing))):
            self.create_line(x,0,x,h,fill='#18212c')
        for y in range(int(self.oy%spacing),max(1,h),max(1,int(spacing))):
            self.create_line(0,y,w,y,fill='#18212c')
        for i,(a,b) in enumerate(self.app.graph.edges):
            if a not in self.app.graph.nodes or b not in self.app.graph.nodes:continue
            color=AMBER if self.app.graph.nodes[a].kind=='rule' else TEAL
            if self.selected_edge==(a,b):color=FG
            self.curve(*self.port(a,'out'),*self.port(b,'in'),color,tags=(f'edge:{i}',))
        f=self.app.font_family;fs=max(8,int(10*self.zoom));small=max(7,int(9*self.zoom))
        for nid,n in self.app.graph.nodes.items():
            x,y=self.xy(n.x,n.y);ww=NODE_W*self.zoom;hh=NODE_H*self.zoom;c=COLORS[n.kind]
            if x+ww<-30 or y+hh<-30 or x>w+30 or y>h+30:continue
            self.create_rectangle(x+4,y+5,x+ww+4,y+hh+5,fill='#0b1119',outline='')
            self.create_rectangle(x,y,x+ww,y+hh,fill=PANEL,outline=FG if nid==self.selected else LINE,width=2 if nid==self.selected else 1)
            self.create_rectangle(x,y,x+ww,y+5*self.zoom,fill=c,outline='')
            category={'condition':self.app.tr('cat_condition'),'action':self.app.tr('cat_action'),'rule':self.app.tr('cat_rule'),'all':self.app.tr('cat_logic'),'any':self.app.tr('cat_logic'),'not':self.app.tr('cat_logic')}[n.kind]
            self.create_text(x+13*self.zoom,y+17*self.zoom,text=category,fill=c,font=(f,max(7,int(8*self.zoom)),'bold'),anchor='w')
            self.create_text(x+13*self.zoom,y+37*self.zoom,text=self.fitted(node_title(n,self.app.lang),(f,fs,'bold'),ww-24*self.zoom),fill=FG,font=(f,fs,'bold'),anchor='w')
            if n.kind=='rule':
                line=f"{self.app.tr('priority')} {n.priority}   ·   cooldown {n.cooldown}"
                detail={'pl':f'{len(self.app.graph.outgoing(nid))} akcji · nie sekwencja','en':f'{len(self.app.graph.outgoing(nid))} actions · not a sequence','de':f'{len(self.app.graph.outgoing(nid))} Aktionen · keine Sequenz'}[self.app.lang]
            elif n.kind in {'all','any','not'}:
                line={'pl':f'{len(self.app.graph.incoming(nid))} wejść','en':f'{len(self.app.graph.incoming(nid))} inputs','de':f'{len(self.app.graph.incoming(nid))} Eingänge'}[self.app.lang]
                detail={'pl':'Wartość logiczna →','en':'Boolean value →','de':'Boolescher Wert →'}[self.app.lang]
            else:
                line=n.ref.removeprefix('samcnpc:')
                if display_meta(n,self.app.lang).get('advanced'):detail={'pl':'Wymaga aktywnego taska / joba','en':'Requires an active task / job','de':'Erfordert aktiven Task / Job'}[self.app.lang]
                elif n.args:detail=', '.join(f'{k}={str(v).lower() if isinstance(v,bool) else v}' for k,v in n.args.items())
                elif n.kind=='action':detail=' + '.join(display_meta(n,self.app.lang).get('channels',[]))
                else:detail=self.app.tr('no_args')
            self.create_text(x+13*self.zoom,y+62*self.zoom,text=self.fitted(line,('Consolas' if sys.platform=='win32' else 'DejaVu Sans Mono',small),ww-24*self.zoom),fill=MUTED,font=('Consolas' if sys.platform=='win32' else 'DejaVu Sans Mono',small),anchor='w')
            self.create_text(x+13*self.zoom,y+85*self.zoom,text=self.fitted(detail,(f,small),ww-24*self.zoom),fill=MUTED,font=(f,small),anchor='w')
            if n.kind in {'rule','action','all','any','not'}:
                px,py=self.port(nid,'in');r=max(4,6*self.zoom)
                pc=AMBER if n.kind=='action' else TEAL
                self.create_oval(px-r,py-r,px+r,py+r,fill=BG,outline=pc,width=2)
            if n.kind!='action':
                px,py=self.port(nid,'out');r=max(4,6*self.zoom)
                pc=AMBER if n.kind=='rule' else TEAL
                self.create_oval(px-r,py-r,px+r,py+r,fill=pc,outline=pc)
        self.create_text(16,18,anchor='w',text=self.app.tr('canvas_header'),fill=MUTED,font=(f,8,'bold'))
        self.create_text(w-16,h-16,anchor='e',text=f"{round(self.zoom*100)}%  ·  {self.app.tr('canvas_hint')}",fill=MUTED,font=(f,8))
        if self.pending:self.create_text(16,h-16,anchor='w',text=self.app.tr('connect_hint'),fill=TEAL,font=(f,9,'bold'))

class Studio(tk.Tk):
    def __init__(self, language: str = DEFAULT_LANGUAGE):
        super().__init__();self.title('SAMCNPC Behavior Studio 1.3.0');self.geometry('1540x930');self.minsize(1080,700)
        self.configure(bg=BG)
        self.lang = language if language in LANGUAGES else DEFAULT_LANGUAGE
        self.language_name = tk.StringVar(self, value=LANGUAGES[self.lang])
        # Keep widgets alive during language changes. Destroying the active native
        # menu/combobox from its own callback is unsafe on some Tk/Windows builds.
        self._localized_widgets = WeakKeyDictionary()
        self._menu_labels = []
        self._example_menu_labels = []
        self._reporting_error = False
        families=set(tkfont.families());self.font_family='Segoe UI' if 'Segoe UI' in families else 'DejaVu Sans'
        self.option_add('*Font',(self.font_family,10));self.option_add('*Menu.font',(self.font_family,10))
        self.option_add('*TCombobox*Listbox.background',INPUT);self.option_add('*TCombobox*Listbox.foreground',FG)
        self._style();self.graph=load_example(next(iter(EXAMPLES)));self.undo_stack=[];self.redo_stack=[];self.file=None;self.dirty=False;self._inspector_fields={};self._inspector_initial={};self._json_rendered=None;self._meta_rendered=None;self._refreshing=False
        self.auto_channels=tk.BooleanVar(value=True);self.status=tk.StringVar();self.npc=tk.StringVar(value='Sam');self.instance=tk.StringVar()
        self._menus();self._build();self.changed(False);self.update_idletasks();self.canvas.fit()
        self.bind('<Control-s>',lambda e:self.save_project());self.bind('<Control-o>',lambda e:self.open_file())
        self.bind('<Control-z>',self.undo_event);self.bind('<Control-y>',self.redo_event)
        self.bind('<F1>',lambda e:self.tabs.select(self.help_tab));self.protocol('WM_DELETE_WINDOW',self.close_app)
    def tr(self,key,**fmt):
        return ui_tr(self.lang,key,**fmt)
    def loc(self,pl,en,de):
        return {'pl':pl,'en':en,'de':de}[self.lang]
    def set_language(self, event=None):
        """Translate in place; never rebuild the widget tree or cancel Tk timers.

        In particular the language selector and its native popup must survive the
        callback. User data, editor drafts, history, tab and viewport are unchanged.
        """
        code = next((k for k, v in LANGUAGES.items() if v == self.language_name.get()), None)
        if code is None:
            self.language_name.set(LANGUAGES[self.lang])
            return
        if code == self.lang:
            return
        self.lang = code
        mission_window = getattr(self, 'mission_window', None)
        if mission_window is not None and mission_window.winfo_exists():
            mission_window.translate()
        for widget, resolver in list(self._localized_widgets.items()):
            if widget.winfo_exists():
                widget.configure(text=resolver())
            else:
                self._localized_widgets.pop(widget, None)
        for menu, index, key in self._menu_labels:
            menu.entryconfigure(index, label=self.tr(key))
        for menu, index, name in self._example_menu_labels:
            menu.entryconfigure(index, label=example_label(self.lang, name))
        for widget, key in self._tab_labels:
            self.tabs.tab(widget, text=self.tr(key))
        self.populate_palette()
        self._refresh_action_labels()
        self._set_readonly_text(self.help_text, HELP.get(self.lang, HELP[DEFAULT_LANGUAGE]))
        self.update_install()
        # Refresh only the report, never JSON text/cursor/undo or uncommitted drafts.
        self.update_json(rewrite=False)
        self.canvas.draw()
        self.notify(self.tr('status_counts', conditions=len(CONDITIONS),
                            actions=len(ACTIONS), builtins=len(BUILTINS)))

    def _translated(self, widget_type, parent, key, **options):
        return self._dynamic_text(widget_type, parent, lambda: self.tr(key), **options)

    def _dynamic_text(self, widget_type, parent, resolver, **options):
        widget = widget_type(parent, text=resolver(), **options)
        self._localized_widgets[widget] = resolver
        return widget

    def _menu_entry(self, parent_menu, kind, key, **options):
        parent_menu.add(kind, label=self.tr(key), **options)
        self._menu_labels.append((parent_menu, parent_menu.index('end'), key))

    def _argument_label(self, node, key):
        spec = self.catalog_meta(node)['args'][key]
        suffix = ' *' if spec['required'] else self.loc(' (opcjonalne)', ' (optional)', ' (optional)')
        default = self.tr('default', value=spec['default']) if 'default' in spec else ''
        return spec['label'] + suffix + default

    def _refresh_action_labels(self):
        # Inspector list items have no text option; replace labels without
        # recreating the listbox or dropping its selection/scroll position.
        info = getattr(self, '_inspector_action_list', None)
        if info is None:
            return
        rule_id, widget = info
        if not widget.winfo_exists():
            return
        selected, view = widget.curselection(), widget.yview()
        widget.delete(0, 'end')
        for action_id in self.graph.outgoing(rule_id):
            widget.insert('end', self.node_title(self.graph.nodes[action_id]))
        for index in selected:
            if index < widget.size():
                widget.selection_set(index)
        if view:
            widget.yview_moveto(view[0])

    @staticmethod
    def _set_readonly_text(widget, text):
        view = widget.yview()
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', text)
        widget.configure(state='disabled')
        if view:
            widget.yview_moveto(view[0])

    def report_callback_exception(self, exc, value, tb):
        """Tk callback exceptions do not reach the try/except around mainloop."""
        detail = ''.join(traceback.format_exception(exc, value, tb))
        path = log_exception(detail, self)
        if self._reporting_error:
            return
        self._reporting_error = True
        try:
            location = str(path) if path else self.tr('error_log_console')
            messagebox.showerror('SAMCNPC Behavior Studio',
                self.tr('callback_error', path=location) + '\n\n' + detail[-2000:], parent=self)
        except tk.TclError:
            pass
        finally:
            self._reporting_error = False

    def catalog_meta(self,node):
        return display_meta(node,self.lang)
    def node_title(self,node):
        return node_title(node,self.lang)
    def _style(self):
        s=ttk.Style(self);s.theme_use('clam')
        s.configure('.',background=PANEL,foreground=FG,font=(self.font_family,10),bordercolor=LINE,lightcolor=LINE,darkcolor=LINE,troughcolor=BG)
        s.configure('TFrame',background=PANEL);s.configure('Root.TFrame',background=BG)
        s.configure('TLabel',background=PANEL,foreground=FG);s.configure('Muted.TLabel',foreground=MUTED)
        s.configure('TButton',padding=(10,7),background=LINE,borderwidth=0)
        s.map('TButton',background=[('active','#3b5067')],foreground=[('disabled',MUTED)])
        s.configure('Accent.TButton',background='#225d54',foreground=FG);s.map('Accent.TButton',background=[('active','#2e7b6d')])
        s.configure('TEntry',fieldbackground=INPUT,foreground=FG,insertcolor=FG,padding=5)
        s.configure('TCombobox',fieldbackground=INPUT,foreground=FG,padding=4,arrowcolor=MUTED)
        s.map('TCombobox',fieldbackground=[('readonly',INPUT)],foreground=[('readonly',FG)])
        s.configure('TNotebook',background=BG,borderwidth=0);s.configure('TNotebook.Tab',padding=(20,10),background=PANEL,foreground=MUTED)
        s.map('TNotebook.Tab',background=[('selected',LINE)],foreground=[('selected',FG)])
        s.configure('Treeview',background=INPUT,fieldbackground=INPUT,foreground=FG,rowheight=29,borderwidth=0)
        s.map('Treeview',background=[('selected','#285c59')]);s.configure('Treeview.Heading',background=PANEL)
        s.configure('TCheckbutton',background=PANEL,foreground=FG);s.map('TCheckbutton',background=[('active',PANEL)])
        s.configure('TSpinbox',fieldbackground=INPUT,foreground=FG,arrowcolor=MUTED)
        s.configure('TLabelframe',background=PANEL,bordercolor=LINE);s.configure('TLabelframe.Label',foreground=MUTED,background=PANEL)
    def _menus(self):
        bar = tk.Menu(self, bg=PANEL, fg=FG, tearoff=False)
        self.menu_bar = bar
        self.configure(menu=bar)
        f = tk.Menu(bar, tearoff=False, bg=PANEL, fg=FG)
        self._menu_entry(bar, 'cascade', 'file', menu=f)
        for key, cmd in [('new', self.new), ('open', self.open_file),
                         ('save', self.save_project), ('save_as', lambda: self.save_project(True)),
                         ('export_json', self.export_json), ('export_zip', self.export_bundle), ('refresh_catalog', self.load_component_catalog)]:
            self._menu_entry(f, 'command', key, command=cmd)
        f.add_separator()
        f.add_command(label='Mission / Misja / Mission…', command=self.open_mission)
        self._menu_entry(f, 'command', 'close', command=self.close_app)
        ex = tk.Menu(bar, tearoff=False, bg=PANEL, fg=FG)
        self._menu_entry(bar, 'cascade', 'examples', menu=ex)
        for name in EXAMPLES:
            ex.add_command(label=example_label(self.lang, name), command=lambda name=name: self.example(name))
            self._example_menu_labels.append((ex, ex.index('end'), name))
        edit = tk.Menu(bar, tearoff=False, bg=PANEL, fg=FG)
        self._menu_entry(bar, 'cascade', 'edit', menu=edit)
        for key, cmd in [('undo', self.undo), ('redo', self.redo),
                         ('auto_layout', self.layout), ('fit_view', lambda: self.canvas.fit())]:
            self._menu_entry(edit, 'command', key, command=cmd)
        lang = tk.Menu(bar, tearoff=False, bg=PANEL, fg=FG)
        self.language_menu = lang
        self._menu_entry(bar, 'cascade', 'language', menu=lang)
        for code, name in LANGUAGES.items():
            lang.add_radiobutton(label=name, variable=self.language_name,
                                value=name, command=self.set_language)

    def open_mission(self):
        from mission_ui import MissionWindow
        window = getattr(self, 'mission_window', None)
        if window is not None and window.winfo_exists():
            window.lift()
        else:
            self.mission_window = MissionWindow(self)

    def _build(self):
        head=ttk.Frame(self,padding=(20,14));head.pack(fill='x')
        left=ttk.Frame(head);left.pack(side='left')
        ttk.Label(left,text='SAMCNPC',font=(self.font_family,20,'bold'),foreground=TEAL).pack(anchor='w')
        self._translated(ttk.Label,left,'header_subtitle',style='Muted.TLabel',font=(self.font_family,9)).pack(anchor='w')
        langbox=ttk.Combobox(head,values=list(LANGUAGES.values()),textvariable=self.language_name,state='readonly',width=10)
        self.language_box=langbox
        langbox.pack(side='right',padx=(12,2));langbox.bind('<<ComboboxSelected>>',self.set_language)
        self._translated(ttk.Button,head,'btn_export_zip',command=self.export_bundle).pack(side='right',padx=4)
        self._translated(ttk.Button,head,'btn_export_json',style='Accent.TButton',command=self.export_json).pack(side='right',padx=4)
        self._translated(ttk.Button,head,'btn_validate',command=self.validate).pack(side='right',padx=4)
        self._translated(ttk.Button,head,'btn_save',command=self.save_project).pack(side='right',padx=4)
        self.tabs=ttk.Notebook(self);self.tabs.pack(fill='both',expand=True,padx=12,pady=(0,8))
        self.editor=ttk.Frame(self.tabs);self.json_tab=ttk.Frame(self.tabs);self.install_tab=ttk.Frame(self.tabs);self.help_tab=ttk.Frame(self.tabs);self.about_tab=ttk.Frame(self.tabs)
        self._tab_labels=[(self.editor,'tab_graph'),(self.json_tab,'tab_json'),(self.install_tab,'tab_install'),(self.help_tab,'tab_help'),(self.about_tab,'tab_about')]
        for widget,key in self._tab_labels:self.tabs.add(widget,text=self.tr(key))
        pane=ttk.Panedwindow(self.editor,orient='horizontal');pane.pack(fill='both',expand=True)
        palette=ttk.Frame(pane,padding=10,width=245);center=ttk.Frame(pane);right=ttk.Frame(pane,padding=12,width=310)
        pane.add(palette,weight=0);pane.add(center,weight=1);pane.add(right,weight=0)
        self.update_idletasks();pane.sashpos(0,245);pane.sashpos(1,max(800,self.winfo_width()-325))
        self._translated(ttk.Label,palette,'node_library',font=(self.font_family,10,'bold')).pack(anchor='w',pady=(0,8))
        self.search=tk.StringVar();entry=ttk.Entry(palette,textvariable=self.search);entry.pack(fill='x',pady=(0,8));entry.bind('<KeyRelease>',lambda e:self.populate_palette())
        pf=ttk.Frame(palette);pf.pack(fill='both',expand=True)
        self.palette=ttk.Treeview(pf,show='tree',selectmode='browse',height=14);self.palette.pack(side='left',fill='both',expand=True)
        ps=ttk.Scrollbar(pf,orient='vertical',command=self.palette.yview);ps.pack(side='right',fill='y');self.palette.configure(yscrollcommand=ps.set)
        self.palette.bind('<Double-1>',lambda e:self.add_from_palette())
        self._translated(ttk.Button,palette,'add_selected',command=self.add_from_palette).pack(fill='x',pady=8)
        self._translated(ttk.Label,palette,'rules_in_pack',font=(self.font_family,9,'bold'),foreground=MUTED).pack(anchor='w',pady=(4,4))
        self.rules=ttk.Treeview(palette,show='tree',selectmode='browse',height=4);self.rules.pack(fill='x')
        self.rules.bind('<<TreeviewSelect>>',self.select_rule)
        self._translated(ttk.Button,palette,'new_rule',command=lambda:self.add_node('rule')).pack(fill='x',pady=(8,0))
        self.populate_palette()
        tools=ttk.Frame(center,padding=(9,6));tools.pack(fill='x')
        for key,cmd in [('tool_undo',self.undo),('tool_redo',self.redo),('tool_layout',self.layout),('tool_fit',lambda:self.canvas.fit()),('tool_delete',self.delete_selected)]:self._translated(ttk.Button,tools,key,command=cmd).pack(side='left',padx=3)
        self.canvas=GraphCanvas(center,self);self.canvas.pack(fill='both',expand=True)
        legend=ttk.Frame(center,padding=(10,7));legend.pack(fill='x')
        self._translated(ttk.Label,legend,'legend_condition',foreground=TEAL).pack(side='left');self._translated(ttk.Label,legend,'legend_rule',foreground=BLUE).pack(side='left');self._translated(ttk.Label,legend,'legend_action',foreground=AMBER).pack(side='left')
        self._translated(ttk.Label,legend,'offline_snapshot',style='Muted.TLabel').pack(side='right')
        rc=tk.Canvas(right,bg=PANEL,highlightthickness=0);rs=ttk.Scrollbar(right,command=rc.yview);rc.configure(yscrollcommand=rs.set)
        rs.pack(side='right',fill='y');rc.pack(fill='both',expand=True)
        rframe=ttk.Frame(rc);win=rc.create_window((0,0),window=rframe,anchor='nw')
        rframe.bind('<Configure>',lambda e:rc.configure(scrollregion=rc.bbox('all')));rc.bind('<Configure>',lambda e:rc.itemconfigure(win,width=e.width))
        self.meta_frame=ttk.Frame(rframe);self.meta_frame.pack(fill='x')
        self._translated(ttk.Label,self.meta_frame,'pack',font=(self.font_family,10,'bold')).pack(anchor='w')
        self.pack_id=tk.StringVar();self.pack_priority=tk.StringVar();self.pack_desc=tk.StringVar()
        for key,var in [('pack_id',self.pack_id),('pack_priority',self.pack_priority),('description',self.pack_desc)]:
            self._translated(ttk.Label,self.meta_frame,key,style='Muted.TLabel').pack(anchor='w',pady=(7,2));ttk.Entry(self.meta_frame,textvariable=var).pack(fill='x')
        self._translated(ttk.Checkbutton,self.meta_frame,'auto_channels',variable=self.auto_channels,command=self.toggle_channels).pack(anchor='w',pady=8)
        chframe=ttk.Frame(self.meta_frame);chframe.pack(fill='x');self.channel_vars={}
        for i,c in enumerate(CHANNELS):
            var=tk.BooleanVar();self.channel_vars[c]=var
            ttk.Checkbutton(chframe,text=c,variable=var,command=self.manual_channels).grid(row=i//2,column=i%2,sticky='w')
        self._translated(ttk.Button,self.meta_frame,'apply_pack',command=self.apply_metadata).pack(fill='x',pady=(8,12))
        ttk.Separator(rframe).pack(fill='x',pady=(0,12))
        self.inspector=ttk.Frame(rframe);self.inspector.pack(fill='both',expand=True)
        self._text_tab(self.json_tab)
        self._installation_tab()
        helptext=self.text_box(self.help_tab,wrap='word');helptext.pack(fill='both',expand=True,padx=16,pady=14)
        self.help_text=helptext
        helptext.insert('1.0',HELP.get(self.lang,HELP[DEFAULT_LANGUAGE]));helptext.configure(state='disabled')
        self._about_tab()
        ttk.Label(self,textvariable=self.status,background=BG,foreground=MUTED,padding=(16,5)).pack(fill='x')
        self.tabs.bind('<<NotebookTabChanged>>',self.tab_changed)
    def _about_tab(self):
        frame=ttk.Frame(self.about_tab,padding=28);frame.pack(fill='both',expand=True)
        logo_path=Path(__file__).resolve().parent/'assets'/'samcnpc_behavior_studio_logo.png'
        self.about_logo=None
        try:
            image=tk.PhotoImage(master=self,file=str(logo_path))
            factor=max(1,(image.width()+719)//720)
            if factor>1:image=image.subsample(factor,factor)
            self.about_logo=image
            ttk.Label(frame,image=image).pack(anchor='center',pady=(4,18))
        except tk.TclError:
            ttk.Label(frame,text='SAMCNPC',font=(self.font_family,28,'bold'),foreground=TEAL).pack(anchor='center',pady=(12,4))
        self._translated(ttk.Label,frame,'about_title',font=(self.font_family,20,'bold')).pack(anchor='center')
        self._translated(ttk.Label,frame,'about_desc',style='Muted.TLabel',wraplength=900,justify='center').pack(anchor='center',pady=(12,14))
        self._translated(ttk.Label,frame,'about_version',foreground=TEAL).pack(anchor='center',pady=2)
        self._translated(ttk.Label,frame,'about_languages',style='Muted.TLabel').pack(anchor='center',pady=2)
        self._translated(ttk.Label,frame,'about_license',style='Muted.TLabel').pack(anchor='center',pady=(2,12))
    def text_box(self,parent,**kwargs):
        from tkinter.scrolledtext import ScrolledText
        return ScrolledText(parent,bg=INPUT,fg=FG,insertbackground=TEAL,selectbackground='#325b70',relief='flat',padx=14,pady=12,undo=True,font=('Consolas' if sys.platform=='win32' else 'DejaVu Sans Mono',10),**kwargs)
    def _text_tab(self,parent):
        bar=ttk.Frame(parent,padding=10);bar.pack(fill='x')
        self._translated(ttk.Button,bar,'json_refresh',command=self.refresh_json).pack(side='left',padx=4)
        self._translated(ttk.Button,bar,'json_apply',command=self.apply_json).pack(side='left',padx=4)
        self._translated(ttk.Button,bar,'copy_json',command=lambda:self.copy(self.json_text.get('1.0','end-1c'))).pack(side='left',padx=4)
        self._translated(ttk.Label,bar,'json_draft_note',style='Muted.TLabel').pack(side='right')
        split=ttk.Panedwindow(parent,orient='vertical');split.pack(fill='both',expand=True,padx=10,pady=(0,10))
        self.json_text=self.text_box(split,wrap='none',height=20);self.report_text=self.text_box(split,wrap='word',height=8)
        split.add(self.json_text,weight=3);split.add(self.report_text,weight=1)
    def _installation_tab(self):
        frame=ttk.Frame(self.install_tab,padding=24);frame.pack(fill='both',expand=True)
        self._translated(ttk.Label,frame,'install_title',font=(self.font_family,18,'bold')).pack(anchor='w')
        self._translated(ttk.Label,frame,'install_desc',style='Muted.TLabel',wraplength=1000).pack(anchor='w',pady=(10,18))
        row=ttk.Frame(frame);row.pack(fill='x')
        ttk.Entry(row,textvariable=self.instance).pack(side='left',fill='x',expand=True,padx=(0,8));self._translated(ttk.Button,row,'choose_instance',command=self.choose_instance).pack(side='left')
        row2=ttk.Frame(frame);row2.pack(fill='x',pady=10)
        self._translated(ttk.Label,row2,'npc_label').pack(side='left');ttk.Entry(row2,textvariable=self.npc,width=22).pack(side='left',padx=10)
        self._translated(ttk.Button,row2,'install_current',style='Accent.TButton',command=self.install_pack).pack(side='left',padx=6)
        self._translated(ttk.Button,row2,'install_zip',command=lambda:self.install_pack('zip')).pack(side='left',padx=6)
        self._translated(ttk.Button,row2,'refresh_instructions',command=self.update_install).pack(side='left',padx=6)
        self.install_text=self.text_box(frame,wrap='word',height=20);self.install_text.pack(fill='both',expand=True,pady=10)
        self._translated(ttk.Button,frame,'copy_commands',command=self.copy_commands).pack(anchor='w')
    def populate_palette(self):
        selected = self.palette.selection()
        view = self.palette.yview()
        expanded = {i: self.palette.item(i, 'open') for i in self.palette.get_children()}
        self.palette.delete(*self.palette.get_children());self.palette_map={}
        q=self.search.get().lower().strip()
        groups=[('logic',self.tr('cat_logic').title(), [('rule',self.tr('new_rule_title')),('all',self.tr('logic_all')),('any',self.tr('logic_any')),('not',self.tr('logic_not'))]),
                ('condition',self.tr('cat_condition').title()+'s' if self.lang=='en' else self.tr('cat_condition').title(),CATALOG['conditions']),
                ('action',self.tr('cat_action').title()+'s' if self.lang=='en' else self.tr('cat_action').title(),[m for m in CATALOG['actions'] if not m['advanced']]),
                ('advanced',{'pl':'Mosty tasków / demo','en':'Task / demo bridges','de':'Task-/Demo-Brücken'}[self.lang],[m for m in CATALOG['actions'] if m['advanced']])]
        for group,label,items in groups:
            self.palette.insert('','end',iid=group,text=label,open=(True if q else expanded.get(group, group!='advanced')))
            for i,item in enumerate(items):
                if group=='logic':kind,title=item;ref='';desc=title
                else:
                    kind='condition' if group=='condition' else 'action';meta=localized_meta(self.lang,item);title=meta['label'];ref=item['id'];desc=meta['description']
                if q and q not in (title+' '+ref+' '+desc).lower():continue
                iid=group+':'+str(i);self.palette.insert(group,'end',iid=iid,text=title);self.palette_map[iid]=(kind,ref)
        visible_selection = [iid for iid in selected if self.palette.exists(iid)]
        if visible_selection:
            self.palette.selection_set(visible_selection)
        if view:
            self.palette.yview_moveto(view[0])
    def add_from_palette(self):
        selected=self.palette.selection()
        if selected and selected[0] in self.palette_map:self.add_node(*self.palette_map[selected[0]])
    def state(self):return copy.deepcopy(self.graph.to_project())
    def record_before(self,before):
        if before==self.state():return
        self.undo_stack.append(before);self.undo_stack=self.undo_stack[-60:];self.redo_stack.clear()
    def undo_event(self,e):
        if isinstance(e.widget,(tk.Text,tk.Entry,ttk.Entry,ttk.Combobox)):return
        self.undo();return 'break'
    def redo_event(self,e):
        if isinstance(e.widget,(tk.Text,tk.Entry,ttk.Entry,ttk.Combobox)):return
        self.redo();return 'break'
    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.state());self.graph=Graph.from_project(self.undo_stack.pop());self.canvas.selected=None;self.changed();self.inspect()
    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.state());self.graph=Graph.from_project(self.redo_stack.pop());self.canvas.selected=None;self.changed();self.inspect()
    def changed(self,dirty=True):
        if dirty:self.dirty=True
        if self.auto_channels.get():self.graph.channels=self.graph.needed_channels()
        meta=(self.graph.pack_id,self.graph.description,str(self.graph.priority))
        draft=(self.pack_id.get(),self.pack_desc.get(),self.pack_priority.get())
        if not (self._meta_rendered is not None and draft!=self._meta_rendered and meta==self._meta_rendered):
            self.pack_id.set(meta[0]);self.pack_desc.set(meta[1]);self.pack_priority.set(meta[2])
        self._meta_rendered=meta
        for c,var in self.channel_vars.items():var.set(c in self.graph.channels)
        self._refreshing=True
        self.rules.delete(*self.rules.get_children())
        for n in self.graph.nodes.values():
            if n.kind=='rule':self.rules.insert('','end',iid=n.id,text=f'{n.priority}  ·  {n.rule_id}')
        self._refreshing=False
        self.canvas.draw();self.inspect();self.update_install();self.update_json(force=False)
        self.title(('● ' if self.dirty else '')+'SAMCNPC Behavior Studio · '+self.graph.pack_id)
        self.notify(self.tr('status_counts',conditions=len(CONDITIONS),actions=len(ACTIONS),builtins=len(BUILTINS)))
    def notify(self,text,error=False):self.status.set((self.tr('error_prefix') if error else '')+text)
    def inspect(self):
        self._inspector_action_list = None
        for w in self.inspector.winfo_children():w.destroy()
        self._inspector_fields={};self._inspector_initial={};nid=self.canvas.selected;n=self.graph.nodes.get(nid)
        self._translated(ttk.Label,self.inspector,'inspector',font=(self.font_family,10,'bold')).pack(anchor='w',pady=(0,8))
        if n is None:
            def label():
                if self.canvas.selected_edge:
                    return self.loc('Wybrane połączenie. Delete usuwa przewód.',
                                    'Connection selected. Delete removes the wire.',
                                    'Verbindung ausgewählt. Delete entfernt die Leitung.')
                return self.tr('select_node')
            self._dynamic_text(ttk.Label,self.inspector,label,style='Muted.TLabel',wraplength=225).pack(anchor='w');return
        self._dynamic_text(ttk.Label,self.inspector,lambda n=n:self.node_title(n),foreground=COLORS[n.kind],font=(self.font_family,12,'bold'),wraplength=230).pack(anchor='w',pady=(0,8))
        if n.kind=='rule':
            fields=[('rule_id','rule_id',n.rule_id),('priority','priority',str(n.priority)),('cooldown','cooldown',str(n.cooldown))]
            for key,label,value in fields:self.inspector_entry(key,label,value)
            self._translated(ttk.Label,self.inspector,'rule_channel_warning',style='Muted.TLabel',wraplength=225).pack(anchor='w',pady=8)
            outs=self.graph.outgoing(nid)
            if outs:
                lb=tk.Listbox(self.inspector,height=min(5,len(outs)),bg=INPUT,fg=FG,selectbackground=LINE,relief='flat',exportselection=False)
                lb.pack(fill='x',pady=5)
                for aid in outs:lb.insert('end',self.node_title(self.graph.nodes[aid]))
                self._inspector_action_list=(nid,lb)
                row=ttk.Frame(self.inspector);row.pack(fill='x')
                for d,key in [(-1,'move_up'),(1,'move_down')]:self._translated(ttk.Button,row,key,command=lambda d=d:self.reorder_action(nid,lb,d)).pack(side='left',padx=2)
        elif n.kind in {'condition','action'}:
            meta=self.catalog_meta(n);ttk.Label(self.inspector,text=n.ref,style='Muted.TLabel',wraplength=225).pack(anchor='w')
            self._dynamic_text(ttk.Label,self.inspector,lambda n=n:self.catalog_meta(n).get('description',''),wraplength=225).pack(anchor='w',pady=8)
            for key,spec in meta.get('args',{}).items():
                self._dynamic_text(ttk.Label,self.inspector,lambda n=n,key=key:self._argument_label(n,key),style='Muted.TLabel',wraplength=225).pack(anchor='w',pady=(7,3))
                value=n.args.get(key,'');var=tk.StringVar(value=str(value).lower() if isinstance(value,bool) else str(value));self._inspector_fields[key]=(var,spec)
                if spec['type']=='boolean':values=['','true','false'];ttk.Combobox(self.inspector,values=values,textvariable=var,state='readonly').pack(fill='x')
                elif 'enum' in spec:ttk.Combobox(self.inspector,values=spec['enum'],textvariable=var,state='readonly').pack(fill='x')
                else:
                    ttk.Entry(self.inspector,textvariable=var).pack(fill='x')
                    if spec['type']=='string':
                        self._dynamic_text(ttk.Label,self.inspector,lambda spec=spec:self.tr('text_length',maximum=spec['maxLength']),style='Muted.TLabel',wraplength=225,font=(self.font_family,8)).pack(anchor='w')
                    else:
                        self._dynamic_text(ttk.Label,self.inspector,lambda spec=spec:self.tr('range',min=spec['minimum'],max=spec['maximum']),style='Muted.TLabel',font=(self.font_family,8)).pack(anchor='w')
            if meta.get('advanced'):self._translated(ttk.Label,self.inspector,'advanced_warning',foreground=AMBER,wraplength=225).pack(anchor='w',pady=8)
        else:
            self._translated(ttk.Label,self.inspector,'logic_help',wraplength=225).pack(anchor='w')
        if self._inspector_fields:self._translated(ttk.Button,self.inspector,'apply_node',command=self.apply_inspector).pack(fill='x',pady=(12,4))
        self._translated(ttk.Button,self.inspector,'delete_node',command=self.delete_selected).pack(fill='x',pady=6)
        self._inspector_initial={k:v[0].get() for k,v in self._inspector_fields.items()}
    def inspector_entry(self,key,label,value):
        self._translated(ttk.Label,self.inspector,label,style='Muted.TLabel').pack(anchor='w',pady=(6,2));var=tk.StringVar(value=value)
        self._inspector_fields[key]=(var,None);ttk.Entry(self.inspector,textvariable=var).pack(fill='x')
    def apply_inspector(self):
        n=self.graph.nodes.get(self.canvas.selected)
        if not n:return
        before=self.state()
        try:
            if n.kind=='rule':
                rid=self._inspector_fields['rule_id'][0].get().strip();p=int(self._inspector_fields['priority'][0].get());cd=int(self._inspector_fields['cooldown'][0].get())
                if not rid or not -100000<=p<=100000 or not 0<=cd<=120000:raise StudioError('Sprawdź ID i zakresy reguły.')
                n.rule_id=rid;n.priority=p;n.cooldown=cd;n.has_cooldown=True
            else:
                args={}
                for k,(var,spec) in self._inspector_fields.items():
                    value=var.get().strip()
                    if not value:
                        if spec['required']:raise StudioError('Wymagany argument '+k)
                        continue
                    args[k]=value if spec['type']=='string' else strict_json(value)
                # Validate the node via a minimal real-shaped pack before committing it.
                trial={'schemaVersion':1,'id':'custom:check','description':'','priority':0,'channels':CHANNELS[:],
                       'rules':[{'id':'check','priority':0,'when':{'test':{'condition':n.ref,'args':args}} if n.kind=='condition' else {'test':{'condition':'samcnpc:always'}},
                                 'actions':[{'action':n.ref,'args':args}] if n.kind=='action' else [{'action':'samcnpc:look_at_summoner'}]}]}
                report=validate_pack(trial)
                if report.errors:raise StudioError('\n'.join(report.errors))
                n.args=args;n.has_args=bool(args)
        except (ValueError,TypeError) as e:
            self.graph=Graph.from_project(before);messagebox.showerror('Parametry',str(e),parent=self);return
        self.record_before(before);self.changed()
    def apply_metadata(self):
        before=self.state()
        try:
            p=int(self.pack_priority.get())
            if not -100000<=p<=100000:raise StudioError('Priorytet poza zakresem -100000..100000.')
            self.graph.pack_id=self.pack_id.get().strip();self.graph.description=self.pack_desc.get();self.graph.priority=p
            if not self.auto_channels.get():self.graph.channels=[c for c,v in self.channel_vars.items() if v.get()]
        except ValueError as e:messagebox.showerror('Dane paczki',str(e),parent=self);return False
        self.record_before(before);self.changed(before!=self.state());return True
    def toggle_channels(self):
        before=self.state()
        if self.auto_channels.get():self.graph.channels=self.graph.needed_channels()
        self.record_before(before);self.changed()
    def manual_channels(self):
        self.auto_channels.set(False);before=self.state();self.graph.channels=[c for c,v in self.channel_vars.items() if v.get()]
        self.record_before(before);self.changed()
    def add_node(self,kind,ref='',position=None):
        if not self.check_drafts():return
        before=self.state()
        if position is None:position=self.canvas.world(self.canvas.winfo_width()/2,self.canvas.winfo_height()/2)
        kwargs={'x':position[0],'y':position[1]}
        if kind=='rule':
            ids={n.rule_id for n in self.graph.nodes.values()};i=1
            while f'rule_{i}' in ids:i+=1
            kwargs['rule_id']=f'rule_{i}'
        elif kind in {'condition','action'}:
            meta=(CONDITIONS if kind=='condition' else ACTIONS)[ref]
            kwargs['args']={k:s['suggested'] for k,s in meta['args'].items() if s['required']};kwargs['has_args']=bool(kwargs['args'])
        try:n=self.graph.add(kind,ref,**kwargs)
        except StudioError as e:messagebox.showerror('Węzeł',str(e),parent=self);return
        self.canvas.selected=n.id;self.canvas.selected_edge=None;self.record_before(before);self.changed();self.canvas.focus_set()
    def delete_selected(self):
        before=self.state()
        if self.canvas.selected:self.graph.remove(self.canvas.selected);self.canvas.selected=None
        elif self.canvas.selected_edge:
            if self.canvas.selected_edge in self.graph.edges:self.graph.edges.remove(self.canvas.selected_edge)
            self.canvas.selected_edge=None
        else:return
        self.canvas.cancel_link();self.record_before(before);self.changed()
    def reorder_action(self,rid,lb,d):
        sel=lb.curselection()
        if not sel:return
        indices=[i for i,(a,b) in enumerate(self.graph.edges) if a==rid];i=sel[0];j=i+d
        if not 0<=j<len(indices):return
        before=self.state();a,b=indices[i],indices[j];self.graph.edges[a],self.graph.edges[b]=self.graph.edges[b],self.graph.edges[a]
        self.record_before(before);self.changed()
    def layout(self):
        if not self.check_drafts():return
        before=self.state();self.graph.layout();self.record_before(before);self.changed();self.canvas.fit()
    def select_rule(self,e):
        if self._refreshing:return
        if self.inspector_pending() and not self.check_drafts():return
        selection=self.rules.selection()
        if not selection:return
        nid=selection[0]
        if nid not in self.graph.nodes:return
        self.canvas.selected=nid;self.canvas.selected_edge=None;self.inspect()
        ids={nid};pending=[nid]
        while pending:
            item=pending.pop()
            for parent in self.graph.incoming(item):
                if parent not in ids:ids.add(parent);pending.append(parent)
        ids.update(self.graph.outgoing(nid));self.canvas.fit(ids)
    def validate(self):
        if not self.check_drafts():return
        if not self.apply_metadata():return
        self.update_json(force=True);self.tabs.select(self.json_tab)
    def update_json(self,force=False,rewrite=True):
        if not hasattr(self,'json_text'):return
        try:
            p=self.graph.to_pack();r=validate_pack(p);text=dump(p)
            lines=[self.loc('WALIDACJA LOKALNA · catalog 2 (nie jest kompilatorem Forge)',
                            'LOCAL VALIDATION · catalog 2 (not the Forge compiler)',
                            'LOKALE PRÜFUNG · Katalog 2 (nicht der Forge-Compiler)'),
                   self.loc(f'Rozmiar: {len(text.encode("utf-8"))} / 131072 bajtów',
                            f'Size: {len(text.encode("utf-8"))} / 131072 bytes',
                            f'Größe: {len(text.encode("utf-8"))} / 131072 Bytes'),
                   self.loc(f'Reguły: {len(p["rules"])} / 256',f'Rules: {len(p["rules"])} / 256',f'Regeln: {len(p["rules"])} / 256'),
                   '\n'+(self.tr('validation_ok') if r.ok else self.loc('EKSPORT ZABLOKOWANY','EXPORT BLOCKED','EXPORT BLOCKIERT'))]
            lines += [self.loc('BŁĄD: ','ERROR: ','FEHLER: ')+x for x in r.errors]
            lines += [self.loc('UWAGA: ','WARNING: ','WARNUNG: ')+x for x in r.warnings]
            lines.append(self.loc('\nOstateczny test w grze: /samcnpc behavior reload',
                                  '\nFinal in-game check: /samcnpc behavior reload',
                                  '\nAbschließende Prüfung im Spiel: /samcnpc behavior reload'))
        except (ValueError,TypeError,RecursionError) as e:
            text='';lines=[self.loc('Graf nie może jeszcze zostać wyeksportowany:','The graph cannot be exported yet:','Der Graph kann noch nicht exportiert werden:'),str(e)]
        current=self.json_text.get('1.0','end-1c')
        if rewrite and (force or self._json_rendered is None or current==self._json_rendered):
            self.json_text.delete('1.0','end');self.json_text.insert('1.0',text);self.json_text.edit_modified(False);self._json_rendered=text
        elif self._json_rendered is not None and current!=self._json_rendered:
            lines.insert(0,self.loc('NIEZASTOSOWANY JSON: podgląd zachowuje Twoją edycję. Użyj JSON → graf; poniższa walidacja dotyczy grafu.',
                                    'UNAPPLIED JSON: the preview preserves your edit. Use JSON → graph; validation below refers to the graph.',
                                    'NICHT ÜBERNOMMENES JSON: Die Vorschau behält deine Änderung. Nutze JSON → Graph; die Prüfung unten betrifft den Graphen.'))
        self._set_readonly_text(self.report_text,'\n\n'.join(lines))
    def refresh_json(self):
        title=self.loc('Odrzucić edycję JSON?','Discard JSON edit?','JSON-Änderung verwerfen?')
        body=self.loc('Zastąpić niezastosowany JSON aktualnym grafem?','Replace unapplied JSON with the current graph?','Nicht übernommenes JSON durch den aktuellen Graphen ersetzen?')
        if self.json_pending() and not messagebox.askyesno(title,body,parent=self):return
        self.update_json(force=True)
    def apply_json(self):
        try:g=Graph.from_pack(strict_json(self.json_text.get('1.0','end-1c')))
        except (ValueError,TypeError) as e:messagebox.showerror('JSON',str(e),parent=self);return
        before=self.state();self.graph=g;self._meta_rendered=None;self._json_rendered=self.json_text.get('1.0','end-1c');self.auto_channels.set(False);self.canvas.selected=None;self.record_before(before);self.changed();self.tabs.select(self.editor);self.canvas.fit()
    def tab_changed(self,e):
        if self.tabs.select()==str(self.install_tab):self.update_install()
    def pending_drafts(self):
        meta=(self.pack_id.get(),self.pack_desc.get(),self.pack_priority.get())
        return (self._meta_rendered is not None and meta!=self._meta_rendered) or self.json_pending() or self.inspector_pending()
    def json_pending(self):
        return self._json_rendered is not None and self.json_text.get('1.0','end-1c')!=self._json_rendered
    def inspector_pending(self):
        return any(v[0].get()!=self._inspector_initial.get(k) for k,v in self._inspector_fields.items())
    def check_drafts(self):
        if self.json_pending():
            messagebox.showwarning(self.loc('Niezastosowany JSON','Unapplied JSON','Nicht übernommenes JSON'),
                                   self.loc('Najpierw użyj JSON → graf albo odśwież Graf → JSON. Eksport nie może po cichu pominąć Twojej edycji.',
                                            'First use JSON → graph or refresh Graph → JSON. Export must not silently ignore your edit.',
                                            'Nutze zuerst JSON → Graph oder aktualisiere Graph → JSON. Der Export darf deine Änderung nicht stillschweigend ignorieren.'),parent=self)
            self.tabs.select(self.json_tab);return False
        if self.inspector_pending():
            messagebox.showwarning(self.loc('Niezastosowane parametry','Unapplied parameters','Nicht übernommene Parameter'),
                                   self.loc('Najpierw kliknij Zastosuj parametry węzła w Inspektorze.','Apply node parameters in Inspector first.','Übernimm zuerst die Knotenparameter im Inspektor.'),parent=self)
            self.tabs.select(self.editor);return False
        return True
    def confirm_discard(self):
        if not self.dirty and not self.pending_drafts():return True
        answer=messagebox.askyesnocancel(self.loc('Niezapisany projekt','Unsaved project','Ungespeichertes Projekt'),
                                         self.loc('Zapisać projekt przed przejściem dalej?','Save the project before continuing?','Projekt vor dem Fortfahren speichern?'),parent=self)
        if answer is None:return False
        if answer:return self.save_project()
        return True
    def new(self):
        if not self.confirm_discard():return
        self._json_rendered=None;self._meta_rendered=None;self.graph=Graph();self.file=None;self.undo_stack=[];self.redo_stack=[];self.canvas.selected=None;self.changed();self.tabs.select(self.editor)
    def example(self,name):
        if not self.confirm_discard():return
        self._json_rendered=None;self._meta_rendered=None;self.graph=load_example(name);self.file=None;self.undo_stack=[];self.redo_stack=[];self.canvas.selected=None;self.auto_channels.set(False);self.dirty=False;self.changed(False)
        self.tabs.select(self.editor);self.canvas.fit()
        if self.graph.pack_id in BUILTINS:
            messagebox.showinfo(self.loc('Referencja drwala','Lumberjack reference','Holzfäller-Referenz'),
                                self.loc('To wbudowana paczka sterująca, nie samodzielna definicja zadania. Oryginalne ID jest blokowane przy eksporcie do config, aby uniknąć duplikatu.',
                                         'This is a built-in controller pack, not a standalone task definition. Exporting its original ID to config is blocked to avoid a duplicate.',
                                         'Dies ist ein eingebautes Controller-Pack, keine eigenständige Task-Definition. Der Export der originalen ID nach config wird blockiert, um Duplikate zu vermeiden.'),parent=self)
    def open_file(self):
        if not self.confirm_discard():return
        path=filedialog.askopenfilename(parent=self,title=self.loc('Otwórz paczkę lub projekt','Open pack or project','Pack oder Projekt öffnen'),filetypes=[('SAMCNPC','*.samgraph *.json'),(self.loc('Wszystkie','All files','Alle Dateien'),'*.*')])
        if not path:return
        try:
            p=Path(path)
            if p.stat().st_size>4*1024*1024:raise StudioError(self.loc('Plik jest za duży.','File is too large.','Datei ist zu groß.'))
            value=strict_json(p.read_text(encoding='utf-8'),project=p.suffix.lower()=='.samgraph')
            project=isinstance(value,dict) and value.get('format')=='samcnpc-studio'
            g=Graph.from_project(value) if project else Graph.from_pack(value)
        except (OSError,ValueError,TypeError,UnicodeError) as e:messagebox.showerror(self.loc('Otwieranie','Open','Öffnen'),str(e),parent=self);return
        self._json_rendered=None;self._meta_rendered=None;self.graph=g;self.file=p if project else None;self.auto_channels.set(False);self.dirty=False;self.undo_stack=[];self.redo_stack=[];self.canvas.selected=None;self.canvas.selected_edge=None;self.canvas.pending=None;self.changed(False);self.tabs.select(self.editor);self.canvas.fit()
    def save_project(self,as_new=False):
        if not self.check_drafts():return False
        if not self.apply_metadata():return False
        path=self.file
        if path is None or as_new:
            name=filedialog.asksaveasfilename(parent=self,title=self.loc('Zapisz projekt edytora','Save editor project','Editor-Projekt speichern'),defaultextension='.samgraph',initialfile=safe_filename(self.graph.pack_id).removesuffix('.json')+'.samgraph',filetypes=[(self.loc('Projekt SAMCNPC','SAMCNPC project','SAMCNPC-Projekt'),'*.samgraph')])
            if not name:return False
            path=Path(name)
        if path.suffix.lower()!='.samgraph':messagebox.showerror(self.loc('Projekt','Project','Projekt'),self.loc('Projekt zapisuj jako .samgraph, nie jako behavior JSON.','Save editor projects as .samgraph, not Behavior JSON.','Editor-Projekte als .samgraph speichern, nicht als Behavior-JSON.'),parent=self);return False
        try:atomic_write(path,dump(self.graph.to_project()))
        except (OSError,ValueError) as e:messagebox.showerror(self.loc('Zapis','Save','Speichern'),str(e),parent=self);return False
        self.file=path;self.dirty=False;self.changed(False);self.notify(self.loc('Zapisano projekt: ','Project saved: ','Projekt gespeichert: ')+str(path));return True
    def prepare_export(self):
        if not self.check_drafts():return None
        if not self.apply_metadata():return None
        try:p,r=require_export(self.graph)
        except (ValueError,TypeError) as e:messagebox.showerror(self.loc('Eksport zablokowany','Export blocked','Export blockiert'),str(e),parent=self);self.tabs.select(self.json_tab);return None
        if r.warnings:
            title=self.loc('Uwagi przed eksportem','Warnings before export','Warnungen vor dem Export')
            suffix=self.loc('\n\nEksportować mimo ostrzeżeń?','\n\nExport despite warnings?','\n\nTrotz Warnungen exportieren?')
            if not messagebox.askokcancel(title,'\n\n'.join(r.warnings[:6])+suffix,parent=self):return None
        return p
    def export_json(self):
        p=self.prepare_export()
        if p is None:return
        name=filedialog.asksaveasfilename(parent=self,title=self.loc('Eksport runtime JSON','Export runtime JSON','Runtime-JSON exportieren'),defaultextension='.json',initialfile=safe_filename(p['id']),filetypes=[('Behavior JSON','*.json')])
        if not name:return
        try:atomic_write(Path(name),dump(p))
        except (OSError,ValueError) as e:messagebox.showerror(self.loc('Eksport','Export','Export'),str(e),parent=self);return
        self.notify(self.loc('Wyeksportowano JSON. Instalacja i polecenia są w zakładce Instalacja.','JSON exported. Installation and commands are in the Install tab.','JSON exportiert. Installation und Befehle stehen im Tab Installation.'))
    def export_bundle(self):
        p=self.prepare_export()
        if p is None:return
        name=filedialog.asksaveasfilename(parent=self,title=self.loc('Eksport paczki Behavior ZIP','Export Behavior Pack ZIP','Behavior-Pack-ZIP exportieren'),defaultextension='.zip',initialfile=safe_filename(p['id']).removesuffix('.json')+'.zip',filetypes=[('ZIP','*.zip')])
        if not name:return
        try:export_zip(Path(name),self.graph,overwrite=True)
        except (OSError,ValueError) as e:messagebox.showerror('ZIP',str(e),parent=self);return
        self.notify(self.loc('Zapisano ZIP. Skopiuj go bez wypakowywania do resources/samcnpc/behaviors/ instancji.','ZIP saved. Copy it without unpacking to the instance resources/samcnpc/behaviors/ directory.','ZIP gespeichert. Ohne Entpacken nach resources/samcnpc/behaviors/ der Instanz kopieren.'))
    def load_component_catalog(self):
        if not self.check_drafts():return
        path=filedialog.askopenfilename(parent=self,title=self.tr('refresh_catalog'),filetypes=[('Registered Behavior schema','*.json')])
        if not path:return
        try:refresh_catalog(Path(path))
        except (OSError,ValueError) as error:messagebox.showerror(self.tr('refresh_catalog'),str(error),parent=self);return
        self._json_rendered=None;self._meta_rendered=None
        self.populate_palette();self.inspect();self.changed(False)
        self.notify(self.tr('catalog_loaded',version=CATALOG['catalogVersion'],conditions=len(CONDITIONS),actions=len(ACTIONS)))
    def choose_instance(self):
        p=filedialog.askdirectory(parent=self,title=self.loc('Wybierz główny katalog instancji gry lub serwera','Choose the game/server instance root','Hauptverzeichnis der Spiel-/Serverinstanz wählen'))
        if p:self.instance.set(p);self.update_install()
    def install_pack(self,format='json'):
        p=self.prepare_export()
        if p is None:return
        if not self.instance.get():self.choose_instance()
        if not self.instance.get():return
        try:destination,pack,r=check_install(self.graph,Path(self.instance.get()),format)
        except (OSError,ValueError) as e:messagebox.showerror(self.tr('tab_install'),str(e),parent=self);return
        extra=self.loc('\nIstniejący plik zostanie zastąpiony; poprzednia wersja trafi do .bak.','\nThe existing file will be replaced; its previous version will be saved as .bak.','\nDie vorhandene Datei wird ersetzt; die vorige Version wird als .json.bak gesichert.') if destination.exists() else ''
        body=self.loc(f'Zapisać paczkę tutaj?\n\n{destination}{extra}\n\nProgram nie uruchomi reload ani assign.',f'Save the pack here?\n\n{destination}{extra}\n\nThe program will not run reload or assign.',f'Pack hier speichern?\n\n{destination}{extra}\n\nDas Programm führt weder reload noch assign aus.')
        if not messagebox.askyesno(self.loc('Potwierdź zapis do instancji','Confirm instance write','Schreiben in Instanz bestätigen'),body,parent=self):return
        try:path=install(self.graph,Path(self.instance.get()),overwrite=True,format=format)
        except (OSError,ValueError) as e:messagebox.showerror(self.tr('tab_install'),str(e),parent=self);return
        self.notify(self.loc('Zainstalowano: ','Installed: ','Installiert: ')+str(path));self.update_install()
        messagebox.showinfo(self.loc('Zapisano','Saved','Gespeichert'),self.loc('W grze wykonaj reload, sprawdź listę paczek, a potem przypisz paczkę bezczynnemu NPC.','Run reload in game, check the pack list, then assign the pack to an idle NPC.','Im Spiel reload ausführen, die Pack-Liste prüfen und das Pack anschließend einem untätigen NPC zuweisen.'),parent=self)
    def update_install(self):
        if not hasattr(self,'install_text'):return
        text=installation_text({'id':self.graph.pack_id},self.lang)
        npc=self.npc.get().strip() or 'Sam';text=text.replace(' Sam ',' '+npc+' ').replace(' Sam\n',' '+npc+'\n')
        if self.graph.pack_id in BUILTINS:text=self.loc('REFERENCJA BUILTIN — NIE INSTALUJ Z TAKIM ID.\n\n','BUILT-IN REFERENCE — DO NOT INSTALL WITH THIS ID.\n\n','BUILT-IN-REFERENZ — NICHT MIT DIESER ID INSTALLIEREN.\n\n')+text
        if self.instance.get():text=self.loc('Instancja: ','Instance: ','Instanz: ')+self.instance.get()+'\n\n'+text
        self._set_readonly_text(self.install_text,text)
    def copy_commands(self):
        npc=self.npc.get().strip()
        if not npc or any(c.isspace() for c in npc):messagebox.showerror('NPC',self.loc('Użyj nazwy bez spacji lub UUID.','Use a name without spaces or a UUID.','Nutze einen Namen ohne Leerzeichen oder eine UUID.'),parent=self);return
        if self.graph.pack_id in BUILTINS:messagebox.showwarning(self.loc('Referencja','Reference','Referenz'),self.loc('To ID jest wbudowane. Nie eksportuj duplikatu do config.','This ID is built in. Do not export a duplicate to config.','Diese ID ist eingebaut. Kein Duplikat nach config exportieren.'),parent=self);return
        self.copy(f'/samcnpc behavior reload\n/samcnpc behavior packs\n/samcnpc behavior assign {npc} {self.graph.pack_id}\n/samcnpc behavior diagnostics {npc}')
    def copy(self,text):self.clipboard_clear();self.clipboard_append(text);self.notify(self.tr('copied'))
    def close_app(self):
        if self.confirm_discard():self.destroy()

def main():
    try:
        if sys.platform=='win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError,OSError):pass
        app=Studio();app.mainloop()
    except Exception:
        error=traceback.format_exc()
        log_exception(error)
        try:messagebox.showerror('SAMCNPC Studio — startup error',error[-3000:])
        except Exception:pass
        raise

if __name__=='__main__':main()
