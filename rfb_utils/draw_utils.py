from . import shadergraph_utils
from ..rman_constants import NODE_LAYOUT_SPLIT
from .. import rman_config
from .. import rfb_icons
import bpy

def _draw_ui_from_rman_config(config_name, panel, context, layout, parent):
    row_dict = dict()
    row = layout.row(align=True)
    col = row.column(align=True)
    row_dict['default'] = col
    rmcfg = rman_config.__RMAN_CONFIG__.get(config_name, None)

    curr_col = col
    for param_name, ndp in rmcfg.params.items():

        if ndp.panel == panel:
            if not hasattr(parent, ndp.name):
                continue

            if hasattr(ndp, 'page') and ndp.page != '':
                # check if we've already drawn page with arrow
                if ndp.page not in row_dict:

                    row = layout.row(align=True)
                    row.label(text=ndp.page)
                    
                    row = layout.row(align=True)
                    col = row.column()

                    row_dict[ndp.page] = col
                    curr_col = col
                else:
                    curr_col = row_dict[ndp.page]
            else:
                curr_col = row_dict['default']

            if hasattr(ndp, 'conditionalVisOps'):
                # check if the conditionalVisOp to see if we're disabled
                expr = ndp.conditionalVisOps['expr']
                node = parent
                if not eval(expr):
                    continue

            label = ndp.label if hasattr(ndp, 'label') else ndp.name
            row = curr_col.row()
            widget = getattr(ndp, 'widget', '')
            options = getattr(ndp, 'options', None)
            if ndp.is_array():
                ui_prop = param_name + "_uio"
                ui_open = getattr(parent, ui_prop)
                icon = 'DISCLOSURE_TRI_DOWN' if ui_open \
                    else 'DISCLOSURE_TRI_RIGHT'

                row.prop(parent, ui_prop, icon=icon, text='',
                            icon_only=True, emboss=False)
                prop = getattr(parent, param_name)      
                prop_meta = node.prop_meta[param_name]                      
                sub_prop_names = list(prop)
                arraylen_nm = '%s_arraylen' % param_name
                arraylen = getattr(parent, arraylen_nm)
                prop_label = prop_meta.get('label', param_name)
                row.label(text=prop_label + ' [%d]:' % arraylen)
                if ui_open:
                    row2 = curr_col.row()
                    col = row2.column()
                    row3 = col.row()      
                    row3.label(text='', icon='BLANK1')                  
                    row3.prop(parent, arraylen_nm, text='Size')
                    for i in range(0, arraylen):
                        row4 = col.row()
                        row4.label(text='', icon='BLANK1')
                        row4.label(text='%s[%d]' % (prop_label, i))
                        row4.prop(parent, '%s[%d]' % (param_name, i), text='')                

                
            elif widget == 'propSearch' and options:
                # use a prop_search layout
                prop_search_parent = options.get('prop_parent')
                prop_search_name = options.get('prop_name')
                if hasattr(ndp, 'page') and ndp.page != '':
                    row.label(text='', icon='BLANK1')
                eval(f'row.prop_search(parent, ndp.name, {prop_search_parent}, "{prop_search_name}", text=label)')               
            else:
                if hasattr(ndp, 'page') and ndp.page != '':
                    row.label(text='', icon='BLANK1')
                row.prop(parent, ndp.name, text=label)    

            if widget in ['fileinput','assetidinput']:                            
                prop_val = getattr(node, prop_name)
                if prop_val != '':
                    row = layout.row(align=True)
                    indented_label(row, None, level)
                    row.prop(node, '%s_colorspace' % prop_name, text='Color Space')
                    rman_icon = rfb_icons.get_icon('rman_txmanager')        
                    row.operator('rman_txmgr_list.open_txmanager', text='', icon_value=rman_icon.icon_id)                     

def _draw_props(node, prop_names, layout):
    for prop_name in prop_names:
        prop_meta = node.prop_meta[prop_name]
        prop = getattr(node, prop_name)
        row = layout.row()
        widget = prop_meta.get('widget', 'default')
        prop_hidden = prop_meta.get('hidden', False)

        if prop_meta['renderman_type'] == 'page':
            ui_prop = prop_name + "_uio"
            ui_open = getattr(node, ui_prop)
            icon = 'DISCLOSURE_TRI_DOWN' if ui_open \
                else 'DISCLOSURE_TRI_RIGHT'

            split = layout.split(factor=NODE_LAYOUT_SPLIT)
            row = split.row()
            row.prop(node, ui_prop, icon=icon, text='',
                     icon_only=True, emboss=False)
            row.label(text=prop_name.split('.')[-1] + ':')

            if ui_open:
                _draw_props(node, prop, layout)

        elif prop_meta['renderman_type'] == 'array':
            ui_prop = prop_name + "_uio"
            ui_open = getattr(node, ui_prop)
            icon = 'DISCLOSURE_TRI_DOWN' if ui_open \
                else 'DISCLOSURE_TRI_RIGHT'

            split = layout.split(factor=NODE_LAYOUT_SPLIT)
            row = split.row()
            for i in range(level):
                row.label(text='', icon='BLANK1')

            row.prop(node, ui_prop, icon=icon, text='',
                        icon_only=True, emboss=False)
            sub_prop_names = list(prop)
            arraylen_nm = '%s_arraylen' % prop_name
            arraylen = getattr(node, arraylen_nm) 
            row.label(text=prop_name + ' [%d]:' % arraylen)

            if ui_open:
                row = layout.row(align=True)
                col = row.column()
                row = col.row()                        
                row.prop(node, arraylen_nm, text='Size')
                for i in range(0, arraylen):
                    row = col.row()
                    row.label(text='%s[%d]' % (prop_name, i))
                    row.prop(node, '%s[%d]' % (prop_name, i), text='')
            continue
        else:
            if widget == 'null' or prop_hidden or prop_name == 'combineMode':
                continue

            row.label(text='', icon='BLANK1')
            # indented_label(row, socket.name+':')
            if "Subset" in prop_name and prop_meta['type'] == 'string':
                row.prop_search(node, prop_name, bpy.data.scenes[0].renderman,
                                "object_groups")
            else:
                row.prop(node, prop_name)   

            if widget in ['fileinput','assetidinput']:                            
                prop_val = getattr(node, prop_name)
                if prop_val != '':
                    row = layout.row(align=True)
                    indented_label(row, None, level)
                    row.prop(node, '%s_colorspace' % prop_name, text='Color Space')
                    rman_icon = rfb_icons.get_icon('rman_txmanager')        
                    row.operator('rman_txmgr_list.open_txmanager', text='', icon_value=rman_icon.icon_id)        


def panel_node_draw(layout, context, id_data, output_type, input_name):
    ntree = id_data.node_tree

    node = shadergraph_utils.find_node(id_data, output_type)
    if not node:
        layout.label(text="No output node")
    else:
        input =  shadergraph_utils.find_node_input(node, input_name)
        #layout.template_node_view(ntree, node, input)
        draw_nodes_properties_ui(layout, context, ntree)

    return True

def draw_nodes_properties_ui(layout, context, nt, input_name='Bxdf',
                             output_node_type="output"):
    output_node = next((n for n in nt.nodes
                        if hasattr(n, 'renderman_node_type') and n.renderman_node_type == output_node_type), None)
    if output_node is None:
        return

    socket = output_node.inputs[input_name]
    node = shadergraph_utils.socket_node_input(nt, socket)

    layout.context_pointer_set("nodetree", nt)
    layout.context_pointer_set("node", output_node)
    layout.context_pointer_set("socket", socket)

    if input_name not in ['Light', 'LightFilter']:
        split = layout.split(factor=0.35)
        split.label(text=socket.name + ':')

        split.context_pointer_set("socket", socket)
        split.context_pointer_set("node", output_node)
        split.context_pointer_set("nodetree", nt)            
        if socket.is_linked:
            rman_icon = rfb_icons.get_icon('out_%s' % node.bl_label)            
            split.menu('NODE_MT_renderman_connection_menu', text='%s (%s)' % (node.name, node.bl_label), icon_value=rman_icon.icon_id)
        else:
            split.menu('NODE_MT_renderman_connection_menu', text='None', icon='NODE_MATERIAL')            

    if node is not None:
        draw_node_properties_recursive(layout, context, nt, node)


def draw_node_properties_recursive(layout, context, nt, node, level=0):


    def indented_label(layout, label, level):
        for i in range(level):
            layout.label(text='', icon='BLANK1')
        if label:
            layout.label(text=label)

    layout.context_pointer_set("node", node)
    layout.context_pointer_set("nodetree", nt)

    def draw_props(prop_names, layout, level):
        for prop_name in prop_names:
            is_pxrramp = node.plugin_name == 'PxrRamp'
            if prop_name == "codetypeswitch":
                row = layout.row()
                if node.codetypeswitch == 'INT':
                    row.prop_search(node, "internalSearch",
                                    bpy.data, "texts", text="")
                elif node.codetypeswitch == 'EXT':
                    row.prop(node, "shadercode")
            elif prop_name == "internalSearch" or prop_name == "shadercode" or prop_name == "expression":
                pass
            else:
                prop_meta = node.prop_meta[prop_name]
                prop = getattr(node, prop_name)
                read_only = prop_meta.get('readOnly', False)
                widget = prop_meta.get('widget', 'default')
                prop_hidden = prop_meta.get('hidden', False)

                if widget == 'null' or prop_hidden:
                    continue
                elif widget == 'colorramp':
                    node_group = bpy.data.node_groups[node.rman_fake_node_group]
                    ramp_name =  prop
                    ramp_node = node_group.nodes[ramp_name]
                    layout.template_color_ramp(
                            ramp_node, 'color_ramp')  
                    continue       
                elif widget == 'floatramp':
                    node_group = bpy.data.node_groups[node.rman_fake_node_group]
                    ramp_name =  prop
                    ramp_node = node_group.nodes[ramp_name]
                    layout.template_curve_mapping(
                            ramp_node, 'mapping')  
                    continue                      

                # double check the conditionalVisOps
                # this might be our first time drawing, i.e.: scene was just opened.
                if 'conditionalVisOps' in prop_meta:
                    cond_expr = prop_meta['conditionalVisOps']['expr']
                    try:
                        hidden = not eval(cond_expr)
                        prop_meta['hidden'] = hidden
                        if hasattr(node, 'inputs') and prop_name in node.inputs:
                            node.inputs[prop_name].hide = hidden
                        if hidden:
                            continue
                    except:                        
                        pass                             

                # else check if the socket with this name is connected
                socket = node.inputs[prop_name] if prop_name in node.inputs \
                    else None
                layout.context_pointer_set("socket", socket)

                if socket and socket.is_linked:
                    input_node = shadergraph_utils.socket_node_input(nt, socket)
                    icon = 'DISCLOSURE_TRI_DOWN' if socket.ui_open \
                        else 'DISCLOSURE_TRI_RIGHT'

                    split = layout.split()
                    row = split.row()
                    indented_label(row, None, level)
                    row.prop(socket, "ui_open", icon=icon, text='',
                             icon_only=True, emboss=False)
                    label = prop_meta.get('label', prop_name)
                    
                    rman_icon = rfb_icons.get_icon('out_%s' % input_node.bl_label)               
                    row.label(text=label + ' (%s):' % input_node.name)
                    row.context_pointer_set("socket", socket)
                    row.context_pointer_set("node", node)
                    row.context_pointer_set("nodetree", nt)
                    row.menu('NODE_MT_renderman_connection_menu', text='', icon_value=rman_icon.icon_id)
                                         
                    if socket.ui_open:
                        draw_node_properties_recursive(layout, context, nt,
                                                       input_node, level=level + 1)

                else:                    
                    row = layout.row(align=True)
                    if prop_meta['renderman_type'] == 'page':
                        if is_pxrramp:
                            # don't' show the old color ramp
                            if prop_name == 'Color Ramp (Manual)':
                                continue
                        ui_prop = prop_name + "_uio"
                        ui_open = getattr(node, ui_prop)
                        icon = 'DISCLOSURE_TRI_DOWN' if ui_open \
                            else 'DISCLOSURE_TRI_RIGHT'

                        split = layout.split(factor=NODE_LAYOUT_SPLIT)
                        row = split.row()
                        indented_label(row, None, level)

                        row.prop(node, ui_prop, icon=icon, text='',
                                 icon_only=True, emboss=False)
                        sub_prop_names = list(prop)
                        if node.bl_idname in {"PxrSurfaceBxdfNode", "PxrLayerPatternOSLNode"}:
                            for pn in sub_prop_names:
                                if pn.startswith('enable'):
                                    row.prop(node, pn, text='')
                                    sub_prop_names.remove(pn)
                                    break

                        row.label(text=prop_name.split('.')[-1] + ':')

                        if ui_open:
                            draw_props(sub_prop_names, layout, level + 1)
                    elif prop_meta['renderman_type'] == 'array':
                        ui_prop = prop_name + "_uio"
                        ui_open = getattr(node, ui_prop)
                        icon = 'DISCLOSURE_TRI_DOWN' if ui_open \
                            else 'DISCLOSURE_TRI_RIGHT'

                        split = layout.split(factor=NODE_LAYOUT_SPLIT)
                        row = split.row()
                        indented_label(row, None, level)

                        row.prop(node, ui_prop, icon=icon, text='',
                                 icon_only=True, emboss=False)
                        sub_prop_names = list(prop)
                        arraylen = getattr(node, '%s_arraylen' % prop_name)
                        prop_label = prop_meta.get('label', prop_name)
                        row.label(text=prop_label + ' [%d]:' % arraylen)

                        if ui_open:
                            level += 1
                            row = layout.row(align=True)
                            col = row.column()
                            row = col.row()
                            indented_label(row, None, level)                     
                            row.prop(node, '%s_arraylen' % prop_name, text='Size')
                            for i in range(0, arraylen):
                                row = layout.row(align=True)
                                col = row.column()                           
                                row = col.row()
                                array_elem_nm = '%s[%d]' % (prop_name, i)
                                indented_label(row, None, level)
                                if array_elem_nm in node.inputs:
                                    op_text = ''
                                    socket = node.inputs[array_elem_nm]
                                    row.context_pointer_set("socket", socket)
                                    row.context_pointer_set("node", node)
                                    row.context_pointer_set("nodetree", nt)

                                    if socket.is_linked:
                                        input_node = shadergraph_utils.socket_node_input(nt, socket)
                                        rman_icon = rfb_icons.get_icon('out_%s' % input_node.bl_label)
                                        row.label(text='%s[%d] (%s):' % (prop_label, i, input_node.name))    
                                        row.menu('NODE_MT_renderman_connection_menu', text='', icon_value=rman_icon.icon_id)
                                        draw_node_properties_recursive(layout, context, nt, input_node, level=level + 1)
                                    else:
                                        row.label(text='%s[%d]: ' % (prop_label, i))
                                        rman_icon = rfb_icons.get_icon('out_unknown')
                                        row.menu('NODE_MT_renderman_connection_menu', text='', icon_value=rman_icon.icon_id)
                        continue
                    else:                      
                        indented_label(row, None, level)
                        
                        if widget == 'propsearch':
                            # use a prop_search layout
                            options = prop_meta['options']
                            prop_search_parent = options.get('prop_parent')
                            prop_search_name = options.get('prop_name')
                            eval(f'row.prop_search(node, prop_name, {prop_search_parent}, "{prop_search_name}")') 
                        elif prop_meta['renderman_type'] in ['struct', 'bxdf', 'vstruct']:
                            row.label(text=prop_meta['label'])
                        elif read_only:
                            # param is read_only i.e.: it is expected that this param has a connection
                            row.label(text=prop_meta['label'])
                            row2 = row.row()
                            row2.prop(node, prop_name, text="", slider=True)
                            row2.enabled=False                           
                        else:
                            row.prop(node, prop_name, slider=True)

                        if prop_name in node.inputs:
                            row.context_pointer_set("socket", socket)
                            row.context_pointer_set("node", node)
                            row.context_pointer_set("nodetree", nt)
                            rman_icon = rfb_icons.get_icon('out_unknown')
                            row.menu('NODE_MT_renderman_connection_menu', text='', icon_value=rman_icon.icon_id)

                    if widget in ['fileinput','assetidinput']:                            
                        prop_val = getattr(node, prop_name)
                        if prop_val != '':
                            row = layout.row(align=True)
                            indented_label(row, None, level)
                            row.prop(node, '%s_colorspace' % prop_name, text='Color Space')
                            rman_icon = rfb_icons.get_icon('rman_txmanager')        
                            from . import texture_utils
                            from . import object_utils
                            id = object_utils.get_context_id(node)
                            nodeID = texture_utils.generate_node_id(node, prop_name, ob=id)
                            op = row.operator('rman_txmgr_list.open_txmanager', text='', icon_value=rman_icon.icon_id)  
                            op.nodeID = nodeID

    # if this is a cycles node do something different
    if not hasattr(node, 'plugin_name') or node.bl_idname == 'PxrOSLPatternNode':
        node.draw_buttons(context, layout)
        for input in node.inputs:
            if input.is_linked:
                input_node = shadergraph_utils.socket_node_input(nt, input)
                icon = 'DISCLOSURE_TRI_DOWN' if input.show_expanded \
                    else 'DISCLOSURE_TRI_RIGHT'

                split = layout.split(factor=NODE_LAYOUT_SPLIT)
                row = split.row()
                indented_label(row, None, level)

                label = input.name                
                rman_icon = rfb_icons.get_icon('out_%s' % input_node.bl_label)
                row.prop(input, "show_expanded", icon=icon, text='',
                         icon_only=True, emboss=False)                                   
                row.label(text=label + ' (%s):' % input_node.name)
                row.context_pointer_set("socket", input)
                row.context_pointer_set("node", node)
                row.context_pointer_set("nodetree", nt)
                row.menu('NODE_MT_renderman_connection_menu', text='', icon_value=rman_icon.icon_id)           

                if input.show_expanded:
                    draw_node_properties_recursive(layout, context, nt,
                                                   input_node, level=level + 1)

            else:
                row = layout.row(align=True)              
                indented_label(row, None, level)
                # indented_label(row, socket.name+':')
                # don't draw prop for struct type
                if input.hide_value:
                    row.label(text=input.name)
                else:
                    row.prop(input, 'default_value',
                             slider=True, text=input.name)

                row.context_pointer_set("socket", input)
                row.context_pointer_set("node", node)
                row.context_pointer_set("nodetree", nt)
                row.menu('NODE_MT_renderman_connection_menu', text='', icon='NODE_MATERIAL')

    else:
        draw_props(node.prop_names, layout, level)
    layout.separator()
