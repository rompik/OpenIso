using GLib;

namespace OpenIso.Core.Drawing {
    public class Sheet : Object {

        /* = Variables = */

        /* = Properties = */
        //** Name of sheet **//
        public string Name { get; set; }

        //** Size of sheet, A3 format by default **//
        // TODO:  Add automatical changing of Width and Height after selecting new size
        // Add list of standard size + Custom for user's size
        public string Size { get; set; default = "A3"; }

        //** Width of sheet **//
        public int Width { get; set; default = 420; }

        //** Height of sheet **//
        public int Height { get; set; default = 297; }

        //** List for storing all shapes of sheet **//
        public Array <GLib.Value?> Shapes { get; set; }

        /* Constructor */
        public Sheet () {

        }

        /* Methods */
        //** Add new shape on sheet - Lines, Circle, Note **//
        public void add_new_shape ( GLib.Variant _new_shape ) {
            this.Shapes.append_val ( _new_shape );
        }
    }
}
