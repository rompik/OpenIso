using OpenIso;
using GLib;

namespace OpenIso.Core.Export {

    public class SVG : GLib.Object {

        //public SVG () {
        public SVG (Core.Drawing.Sheet _sheet) {
        //public SVG (File _file){

            File _svg_file = File.new_for_path (Environment.get_home_dir () + "/Dropbox/VALA/openiso/test/Drawing.svg");

            try {

                if( _svg_file.query_exists() == true){
                    _svg_file.delete(null);
                }

                FileOutputStream fos = _svg_file.create (FileCreateFlags.REPLACE_DESTINATION, null);
                DataOutputStream dos = new DataOutputStream (fos);
                dos.put_string ("""<svg height="297" width="420" xmlns:xlink="http://www.w3.org/1999/xlink">""" + "\n");
                dos.put_string ("""<a xlink:href="http://www.w3schools.com/svg/" target="_blank">""" + "\n");
                dos.put_string ("""<line x1="20" y1="5" x2="20" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                dos.put_string ("""<line x1="20" y1="5" x2="415" y2="5" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                dos.put_string ("""<line x1="415" y1="5" x2="415" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                dos.put_string ("""<line x1="20" y1="292" x2="415" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                dos.put_string ("""<line x1="20" y1="20" x2="415" y2="292" style="stroke:rgb(255,0,0);stroke-width:1" />""" + "\n");
                dos.put_string ("""</a>""" + "\n");
                dos.put_string ("""</svg>""" + "\n");

            } catch (Error e) {

                 stderr.printf ("Error: %s\n", e.message);

            }
        }
    }
}
    
