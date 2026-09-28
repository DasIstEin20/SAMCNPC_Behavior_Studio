"""Native Tk smoke; requires a display (Linux: xvfb-run -a python -m unittest ...)."""
import os
import unittest
from unittest.mock import patch
import sys

@unittest.skipIf(sys.platform.startswith('linux') and not os.environ.get('DISPLAY'),'Brak DISPLAY; test GUI wymaga Xvfb lub pulpitu.')
class GuiTests(unittest.TestCase):
    def setUp(self):
        from studio import Studio
        import traceback
        self.callback_errors = []
        def capture(_app, exc, value, tb):
            self.callback_errors.append(''.join(traceback.format_exception(exc, value, tb)))
        patcher = patch.object(Studio, 'report_callback_exception', capture)
        patcher.start()
        self.addCleanup(patcher.stop)
        # With DISPLAY supplied, a TclError in construction must FAIL, not skip.
        self.app = Studio()
        self.app.tk.createcommand('bgerror', lambda text: self.callback_errors.append('Tcl: ' + str(text)))
        self.app.update(); self.app.canvas.fit(); self.app.update()

    def tearDown(self):
        try:
            self.app.update()
        finally:
            self.app.destroy()
        self.assertEqual(self.callback_errors, [], 'GUI callback/background error was raised')
    def test_start(self):
        self.assertTrue(self.app.canvas.find_all());self.assertEqual(self.app.graph.pack_id,'example:follow')
    def test_ports_mouse_connect_and_delete(self):
        from engine import Graph
        a=self.app;a.graph=Graph();r=a.graph.add('rule',rule_id='a',x=310,y=100);c=a.graph.add('condition','samcnpc:always',x=10,y=100);x=a.graph.add('action','samcnpc:look_at_summoner',x=610,y=100)
        a.changed();a.canvas.fit();a.update()
        for src,dst in [(c.id,r.id),(r.id,x.id)]:
            p=a.canvas.port(src,'out');q=a.canvas.port(dst,'in')
            a.canvas.event_generate('<Button-1>',x=round(p[0]),y=round(p[1]))
            a.canvas.event_generate('<B1-Motion>',x=round(q[0]),y=round(q[1]))
            a.canvas.event_generate('<ButtonRelease-1>',x=round(q[0]),y=round(q[1]));a.update()
        self.assertEqual(len(a.graph.edges),2);self.assertEqual(a.graph.to_pack()['rules'][0]['actions'][0]['action'],'samcnpc:look_at_summoner')
        a.canvas.selected=None;a.canvas.selected_edge=(r.id,x.id);a.delete_selected();self.assertEqual(len(a.graph.edges),1)
        a.undo();self.assertEqual(len(a.graph.edges),2)
    def test_parameter_inspector(self):
        a=self.app;n=next(n for n in a.graph.nodes.values() if n.kind=='action');a.canvas.selected=n.id;a.inspect();a.update()
        a._inspector_fields['stopDistance'][0].set('4.5');a.apply_inspector();self.assertEqual(a.graph.nodes[n.id].args['stopDistance'],4.5)
        a.undo();self.assertEqual(a.graph.nodes[n.id].args['stopDistance'],2)
    def test_json_draft_preserved(self):
        a=self.app;a.json_text.insert('end',' ');draft=a.json_text.get('1.0','end-1c');a.update_json(force=False);self.assertEqual(a.json_text.get('1.0','end-1c'),draft);self.assertTrue(a.json_pending())
    def test_json_import(self):
        a=self.app;raw=a.json_text.get('1.0','end-1c').replace('example:follow','mine:test');a.json_text.delete('1.0','end');a.json_text.insert('1.0',raw);a.apply_json();self.assertEqual(a.graph.pack_id,'mine:test')
    def test_tabs(self):
        for tab in [self.app.json_tab,self.app.install_tab,self.app.help_tab,self.app.about_tab,self.app.editor]:self.app.tabs.select(tab);self.app.update()

    def test_language_switch_and_about(self):
        a=self.app
        self.assertEqual(a.lang,'en')
        a.language_name.set('Polski');a.set_language();a.update()
        a.language_name.set('English');a.set_language();a.update()
        self.assertEqual(a.lang,'en');self.assertIn('Rule graph',a.tabs.tab(a.editor,'text'))
        self.assertIsNotNone(a.about_tab)
        a.language_name.set('Deutsch');a.set_language();a.update()
        self.assertEqual(a.lang,'de');self.assertIn('Regelgraph',a.tabs.tab(a.editor,'text'))
        a.language_name.set('Polski');a.set_language();a.update();self.assertEqual(a.lang,'pl')

    def test_search_and_add(self):
        a=self.app;a.search.set('prepare_field');a.populate_palette();self.assertEqual(len(a.palette_map),1)
        iid=next(iter(a.palette_map));a.palette.selection_set(iid);a.add_from_palette();self.assertTrue(any(n.ref=='samcnpc:run_prepare_field_task' for n in a.graph.nodes.values()))

    def change_language(self, code, via='event'):
        from i18n import LANGUAGES
        a = self.app
        if via == 'menu':
            a.language_menu.invoke(list(LANGUAGES).index(code))
        else:
            a.language_box.set(LANGUAGES[code])
            a.language_box.event_generate('<<ComboboxSelected>>')
        a.update()
        self.assertEqual(a.lang, code)

    def test_english_default_and_fallback(self):
        from i18n import DEFAULT_LANGUAGE, tr
        a = self.app
        self.assertEqual(DEFAULT_LANGUAGE, 'en')
        self.assertEqual(a.lang, 'en')
        self.assertEqual(a.language_name.get(), 'English')
        self.assertEqual(a.tabs.tab(a.editor, 'text'), 'Rule graph')
        self.assertEqual(a.menu_bar.entrycget(0, 'label'), 'File')
        self.assertEqual(tr('invalid', 'file'), 'File')
        self.assertIn('Offline visual editor', a.tr('about_desc'))

    def test_switch_keeps_widget_tree_alive(self):
        a = self.app
        controls = (a.canvas, a.tabs, a.language_box, a.menu_bar, a.language_menu,
                    a.json_text, a.pack_id, a.about_logo, a.help_text)
        for code in ('de', 'pl', 'en') * 4:
            self.change_language(code)
            self.assertEqual(controls, (a.canvas, a.tabs, a.language_box, a.menu_bar,
                              a.language_menu, a.json_text, a.pack_id, a.about_logo, a.help_text))
            self.assertTrue(a.language_box.winfo_exists())
            self.assertTrue(a.canvas.winfo_exists())

    def test_switch_menu_invocation_keeps_menu(self):
        a = self.app
        menu = a.language_menu
        for code in ('pl', 'de', 'en') * 3:
            self.change_language(code, via='menu')
            self.assertIs(a.language_menu, menu)
            self.assertTrue(menu.winfo_exists())

    def test_native_combobox_popup_mouse_selection(self):
        from i18n import LANGUAGES
        a = self.app
        # Aqua uses a native menu rather than this Tk listbox. The virtual-event
        # tests still exercise the application handler on that platform.
        if a.tk.call('tk', 'windowingsystem') == 'aqua':
            self.skipTest('Aqua has a different native popup implementation')
        combo = a.language_box
        for code in ('de', 'pl', 'en') * 3:
            combo.event_generate('<ButtonPress-1>', x=combo.winfo_width()-8,
                                 y=combo.winfo_height()//2)
            a.update()
            popdown = str(a.tk.call('ttk::combobox::PopdownWindow', str(combo)))
            lb = popdown + '.f.l'
            row = tuple(combo.cget('values')).index(LANGUAGES[code])
            bbox = a.tk.call(lb, 'bbox', row)
            self.assertTrue(bbox, 'Dropdown row is not visible')
            x, y, w, h = map(int, bbox)
            # These run Tk's real listbox hover and release bindings (LBSelected),
            # rather than calling Studio.set_language directly.
            # Windows needs the complete listbox click, including its press event.
            a.tk.call('event', 'generate', lb, '<ButtonPress-1>', '-x', x+5, '-y', y+h//2)
            a.tk.call('event', 'generate', lb, '<Motion>', '-x', x+5, '-y', y+h//2)
            a.tk.call('event', 'generate', lb, '<ButtonRelease-1>', '-x', x+5, '-y', y+h//2)
            a.update()
            self.assertEqual(a.lang, code)
            self.assertIs(combo, a.language_box)
            self.assertTrue(combo.winfo_exists())
            self.assertEqual(str(a.tk.call('grab', 'current')), '')

    def test_language_change_preserves_scheduled_callbacks(self):
        a = self.app
        ran = []
        timer = a.after(1000, lambda: ran.append('timer'))
        idle = a.after_idle(lambda: ran.append('idle'))
        try:
            a.language_name.set('Deutsch')
            a.set_language()  # no nested update/after-cancel inside this handler
            pending = a.tk.splitlist(a.tk.call('after', 'info'))
            self.assertIn(timer, pending)
            self.assertIn(idle, pending)
            a.update()
            self.assertIn('idle', ran)
        finally:
            a.after_cancel(timer)

    def test_language_switch_preserves_graph_history_view_and_tab(self):
        a = self.app
        a.add_node('all')
        a.canvas.zoom = 0.73
        a.canvas.ox = -67.0
        a.canvas.oy = 19.0
        selected = a.canvas.selected
        state = a.state()
        undo = list(a.undo_stack)
        dirty = a.dirty
        a.tabs.select(a.about_tab); a.update()
        tab = a.tabs.select()
        for code in ('de', 'pl', 'en'):
            self.change_language(code)
            self.assertEqual(a.state(), state)
            self.assertEqual(a.undo_stack, undo)
            self.assertEqual(a.dirty, dirty)
            self.assertEqual(a.canvas.selected, selected)
            self.assertEqual((a.canvas.zoom, a.canvas.ox, a.canvas.oy), (0.73, -67.0, 19.0))
            self.assertEqual(a.tabs.select(), tab)

    def test_language_switch_preserves_all_unapplied_drafts(self):
        a = self.app
        n = next(n for n in a.graph.nodes.values() if n.kind == 'action')
        a.canvas.selected = n.id; a.inspect(); a.update()
        var = a._inspector_fields['stopDistance'][0]
        var.set('4.5')
        a.pack_desc.set('My unsaved Beschreibung / opis')
        a.pack_id.set('draft:kept')
        a.pack_priority.set('125')
        a.json_text.insert('end', '  ')
        a.json_text.mark_set('insert', '2.3')
        draft = a.json_text.get('1.0', 'end-1c')
        index = a.json_text.index('insert')
        state, initial = a.state(), dict(a._inspector_initial)
        with patch('studio.messagebox.showwarning') as warning:
            for code in ('de', 'pl', 'en'):
                self.change_language(code)
                self.assertEqual(a.json_text.get('1.0', 'end-1c'), draft)
                self.assertEqual(a.json_text.index('insert'), index)
                self.assertEqual(a.pack_desc.get(), 'My unsaved Beschreibung / opis')
                self.assertEqual(a.pack_id.get(), 'draft:kept')
                self.assertEqual(a.pack_priority.get(), '125')
                self.assertIs(a._inspector_fields['stopDistance'][0], var)
                self.assertEqual(var.get(), '4.5')
                self.assertEqual(a._inspector_initial, initial)
                self.assertEqual(a.state(), state)
                self.assertTrue(a.pending_drafts())
            warning.assert_not_called()

    def test_switch_preserves_json_text_undo(self):
        a = self.app
        before = a.json_text.get('1.0', 'end-1c')
        a.json_text.edit_reset()
        a.json_text.insert('end', 'ABC')
        a.json_text.edit_separator()
        self.change_language('de')
        a.json_text.edit_undo()
        self.assertEqual(a.json_text.get('1.0', 'end-1c'), before)

    def test_switch_translates_inspector_without_replacing_inputs(self):
        a = self.app
        n = next(n for n in a.graph.nodes.values() if n.kind == 'action')
        a.canvas.selected = n.id; a.inspect(); a.update()
        inputs = dict(a._inspector_fields)
        self.change_language('de')
        labels = [str(w.cget('text')) for w in a.inspector.winfo_children() if 'text' in w.keys()]
        self.assertIn('Stoppabstand *', labels)
        self.assertTrue(any('Bereich:' in text for text in labels))
        self.assertEqual(a._inspector_fields, inputs)
        self.change_language('pl')
        labels = [str(w.cget('text')) for w in a.inspector.winfo_children() if 'text' in w.keys()]
        self.assertIn('Dystans zatrzymania *', labels)

    def test_all_components_inspected_in_all_languages(self):
        from engine import Graph, CONDITIONS, ACTIONS
        a = self.app
        for kind, components in (('condition', CONDITIONS), ('action', ACTIONS)):
            for ref in components:
                a.graph = Graph()
                n = a.graph.add(kind, ref)
                a.canvas.selected = n.id
                a.inspect()
                for code in ('de', 'pl', 'en'):
                    a.language_name.set({'de':'Deutsch', 'pl':'Polski', 'en':'English'}[code])
                    a.set_language()
                a.update()
                self.assertFalse(a.inspector_pending())

    def test_switch_preserves_rule_action_list_selection(self):
        a = self.app
        r = next(n for n in a.graph.nodes.values() if n.kind == 'rule')
        a.canvas.selected = r.id; a.inspect(); a.update()
        rid, lb = a._inspector_action_list
        lb.selection_set(0)
        self.change_language('de')
        self.assertIs(a._inspector_action_list[1], lb)
        self.assertEqual(lb.curselection(), (0,))
        self.assertIn('Beschwörer', lb.get(0))
        self.assertEqual(a._inspector_fields['rule_id'][0].get(), r.rule_id)

    def test_switch_preserves_search_selection_and_install_fields(self):
        a = self.app
        a.search.set('prepare_field'); a.populate_palette()
        iid = next(iter(a.palette_map)); a.palette.selection_set(iid)
        a.instance.set('C:/Games/Test instance')
        a.npc.set('TestNpc')
        self.change_language('de')
        self.assertEqual(a.search.get(), 'prepare_field')
        self.assertEqual(a.palette.selection(), (iid,))
        self.assertEqual(a.instance.get(), 'C:/Games/Test instance')
        self.assertEqual(a.npc.get(), 'TestNpc')
        self.assertIn('TestNpc', a.install_text.get('1.0', 'end-1c'))

    def test_runtime_export_identical_after_language_changes(self):
        from engine import dump
        a = self.app
        before = dump(a.graph.to_pack())
        for code in ('de', 'pl', 'en'):
            self.change_language(code)
            self.assertEqual(dump(a.graph.to_pack()), before)

    def test_invalid_language_restores_selector(self):
        a = self.app
        a.language_box.set('unknown'); a.set_language()
        self.assertEqual(a.lang, 'en')
        self.assertEqual(a.language_name.get(), 'English')

    def test_fitted_text_respects_pixel_width(self):
        import tkinter.font as tkfont
        canvas = self.app.canvas
        spec = (self.app.font_family, 10)
        font = tkfont.Font(root=self.app, font=spec)
        for text in ('', 'English', 'Gesundheitsanteil', 'Połączenie — żółć', 'W'*128):
            for width in (0, 3, 15, 45, 170, 1000):
                fitted = canvas.fitted(text, spec, width)
                self.assertLessEqual(font.measure(fitted), width)
                self.assertTrue(fitted == text or fitted == '' or fitted.endswith('…'))

    def test_fitted_text_reuses_native_font(self):
        canvas = self.app.canvas
        spec = (self.app.font_family, 11)
        canvas.fitted('A', spec, 120)
        font = canvas._font_cache[spec]
        for i in range(50):
            canvas.fitted('Different label ' + str(i), spec, 120)
        self.assertIs(canvas._font_cache[spec], font)

    def test_fitted_text_cache_is_bounded(self):
        canvas = self.app.canvas
        spec = (self.app.font_family, 10)
        for i in range(2100):
            canvas.fitted('Unique label ' + str(i), spec, 120)
        self.assertLessEqual(len(canvas._fit_cache), 2048)

if __name__=='__main__':unittest.main()
