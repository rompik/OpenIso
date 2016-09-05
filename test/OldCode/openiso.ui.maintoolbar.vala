using Gtk;

namespace OpenIso.UI{
        public class MainToolbar : Gtk.Toolbar {

            public Gtk.ToolButton ButtonOpen;
            public Gtk.ToolButton ButtonSave;

            public MainToolbar(){

                Gtk.Image imgOpen = new Gtk.Image.from_icon_name ("document-open", Gtk.IconSize.SMALL_TOOLBAR);
                Gtk.ToolButton ButtonOpen = new Gtk.ToolButton (imgOpen, null);
                ButtonOpen.is_important = true;

                Gtk.Image imgSave = new Gtk.Image.from_icon_name ("document-save", Gtk.IconSize.SMALL_TOOLBAR);
                Gtk.ToolButton ButtonSave = new Gtk.ToolButton (imgSave, null);
                ButtonSave.is_important = true;

                this.add(ButtonOpen);
                this.add(ButtonSave);

            }
        }
    }



