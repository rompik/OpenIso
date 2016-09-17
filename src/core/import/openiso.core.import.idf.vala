/* openiso.core.import.idf.vala
 *
 * Copyright (C) 2016 Rompik <rompik@mail.ru>
 *
 * This file is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * This file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

using GLib;
using OpenIso.Core;

namespace OpenIso.Core.Import {
    public class IDF : GLib.Object {

        /*
        * Setup variables
        */

        /**
        * New IDF file
        */

        //*String for IDF file path*//
        private Array <string> _file_strings = new Array <string> ();

        //*Array for loaded pipes*//
        private Array <Piping.Pipe> property_pipes = new Array <Piping.Pipe> ();

        //*Array for revisions of loaded pipe*//
        //private Array <Revisions.Revision> _PipeRevisions = new Array <Revisions.Revision> ();

        //*Current number of loaded pipe*//
        private int _iCurPipeNumber = 0;

        //*Next number for future loaded pipe*//
        private int _iNextPipeNumber = 0;

        //*Current number of loaded material*//
        private int _iCurMaterialNumber = 0;

        //*Next number for future loaded material*//
        private int _iNextMaterialNumber = 0;

        //*Current number of component in current pipe*//
        private int _iCurComponentNumber = 0;

        //*Next number for future loaded component in current pipe*//
        private int _iNextComponentNumber = 0;

        //*Current number of loaded note text *//
        private int _iCurNoteTextNumber = 0;

        //*Next number for future loaded note text *//
        private int _iNextNoteTextNumber = 0;

        //*Collection of imported notes*//
        //private Array <string> property_notes = new Array <string> ();
        //private Array <Drawing.Note.Text> property_note_texts = new Array<Drawing.Note.Text> ();
        //private HashMap<int, string> property_note_texts = new HashMap<int, string> ();

        //*Array of imported materials*//
        private Array <MTO.Material> property_materials = new Array <MTO.Material> ();

        //** List of pipes **//
        // Has to use detailed as there is problem with addining new component to array
        public Array <Piping.Pipe> Pipes {
            get { return property_pipes; }
            set { property_pipes = value; }
        }

        //** List of text notes **//
        public Array <Drawing.Note.Text> Texts { get; set; }

        /*
        *   Read IDF file and save data to array of strings
        */
        public IDF (File _file){

            if (!_file.query_exists ()) {
                stderr.printf (_("File '%s' does not exist.\n"), _file.get_path ());
            }

            try {
                /*
                * Open file for reading and wrap returned FileInputStream into
                * a DataInputStream, which will be red line by line
                *
                */
                var dis = new DataInputStream ( _file.read () );

                string line;

                while ((line = dis.read_line (null)) != null){

                    _file_strings.append_val (line);

                }

                CollectData ();

                ApplyMaterial2Component (this.Pipes);

                WriteMTOFile (this.Pipes);

            }

            catch (Error e) {
                error ("%s", e.message);
            }
        }

        // Method to get properties of component from string
        //private HashTable <string, GLib.Variant> component_properties_from_string (string _input, Piping.Component _component) {
        private Piping.Component component_with_properties_from_string (string _input) {

            //* Create dummy component *//
            Piping.Component _component = new Piping.Component();

             //* Create dummy Material *//
            _component.Material = new MTO.Material ();

            //* Collect Data from String *//
            //* (1) - Component Type *//
            string _type = _input.substring(0, 5).strip();

            //* (2) - Start Position East / West - Value is converted to mm *//
            double _start_pos_east = double.parse( _input.substring(6,11).strip() ) / 100;

            //* (3) - Start Position North / South - Value is converted to mm *//
            double _start_pos_north = double.parse( _input.substring(17,10).strip() ) / 100;

            //* (4) - Start Position Eleveation +/- - Value is converted to mm *//
            double _start_pos_elev = double.parse( _input.substring(27,10).strip() ) / 100;

            //* (5) - End Position East / West - Value is converted to mm *//
            double _end_pos_east = double.parse( _input.substring(37,12).strip() ) / 100;

            //* (6) - End Position North / South - Value is converted to mm *//
            double _end_pos_north = double.parse( _input.substring(49,10).strip() ) / 100;

            //* (7) - End Position Eleveation +/- - Value is converted to mm  *//
            double _end_pos_elev = double.parse( _input.substring(59,10).strip() ) / 100;

            //* (8) - Pipe Bore - Value depends from system of units *//
            double _pipe_bore = double.parse( _input.substring(69,8).strip() );

            //* (9) - Material Number -> Item Code *//
            int _item_code_number = int.parse (_input.substring(76,10).strip());

            //* (10) - Component Weight - Value in kgs *//
            double _weight = double.parse(_input.substring(87,8).strip());

            //* (11) - *//
            string _none_1 = _input.substring(69,8).strip();

            //* (12) - Skey Code *//
            string _skey = _input.substring(104,4).strip();

            //* (13) - *//
            string _none_2 = _input.substring(69,8).strip();


            //* Setup component properties *//
            //* Type of Component * //

            switch ( _type ) {

                case "30":

                    _component.Type = "BEND";

                    break;

                case "31":

                    _component.Type = "U-BEND";

                    break;

                case "35":

                    _component.Type = "ELBOW";

                    break;

                case "36":

                    _component.Type = "REDUCING ELBOW";

                    break;

                case "40":

                    _component.Type = "OLET";

                    break;

                case "41":

                    _component.Type = "OLET";

                    break;

                case "42":

                    _component.Type = "OLET";

                    break;

                case "45":

                    _component.Type = "TEE";

                    break;

                case "46":

                    _component.Type = "TEE-SET-ON";

                    break;

                case "47":

                    _component.Type = "TEE-STUB";

                    break;

                case "50":

                    _component.Type = "CROSS";

                    break;

                case "51":

                    _component.Type = "CROSS";

                    break;

                case "52":

                    _component.Type = "CROSS";

                    break;

                case "53":

                    _component.Type = "CROSS";

                    break;

                case "55":

                    _component.Type = "REDUCER";

                    break;

                case "60":

                    _component.Type = "REDUCER-CONCETRIC-TEED";

                    break;

                case "61":

                    _component.Type = "REDUCER-CONCETRIC-TEED";

                    break;

                case "62":

                    _component.Type = "REDUCER-CONCETRIC-TEED";

                    break;

                case "65":

                    _component.Type = "FLANGE-REDUCING-CONCETRIC";

                    break;

                case "70":

                    _component.Type = "TEE-BEND";

                    break;

                case "71":

                    _component.Type = "TEE-BEND";

                    break;

                case "72":

                    _component.Type = "TEE-BEND";

                    break;

                case "75":

                    _component.Type = "VALVE-ANGLE";

                    break;

                case "76":

                    _component.Type = "VALVE-ANGLE";

                    break;

                case "80":

                    _component.Type = "VALVE-3WAY";

                    break;

                case "81":

                    _component.Type = "VALVE-3WAY";

                    break;

                case "82":

                    _component.Type = "VALVE-3WAY";

                    break;

                case "85":

                    _component.Type = "VALVE-4WAY";

                    break;

                case "86":

                    _component.Type = "VALVE-4WAY";

                    break;

                case "87":

                    _component.Type = "VALVE-4WAY";

                    break;

                case "90":

                    _component.Type = "INSTRUMENT-DIAL";

                    break;

                case "91":

                    _component.Type = "INSTRUMENT";

                    break;

                case "92":

                    _component.Type = "INSTRUMENT";

                    break;

                case "93":

                    _component.Type = "INSTRUMENT";

                    break;

                case "95":

                    _component.Type = "MISC-COMPONENT";

                    break;

                case "96":

                    _component.Type = "MISC-COMPONENT";

                    break;

                case "100":

                    _component.Type = "TUBE";

                    break;

                case "101":

                    _component.Type = "TUBE-FIXED";

                    break;

                case "102":

                    _component.Type = "TUBE-BLOCK-FIXED";

                    break;

                case "103":

                    _component.Type = "TUBE-BLOCK-VARIABLE";

                    break;

                case "104":

                    _component.Type = "GAP";

                    break;

                case "105":

                    _component.Type = "FLANGE";

                    break;

                case "106":

                    _component.Type = "LAPJOINT";

                    break;

                case "107":

                    _component.Type = "FLANGE-BLIND";

                    break;

                case "110":

                    _component.Type = "GASKET";

                    break;

                case "111":

                    _component.Type = "CONNECTOR";

                    break;

                case "112":

                    _component.Type = "NUT";

                    break;

                case "113":

                    _component.Type = "CLAMP";

                    break;

                case "114":

                    _component.Type = "MISC-HYGIENIC";

                    break;

                case "115":

                    _component.Type = "BOLT";

                    break;

                case "120":

                    _component.Type = "WELD";

                    break;

                case "125":

                    _component.Type = "CAP";

                    break;

                case "126":

                    _component.Type = "COUPLING";

                    break;

                case "127":

                    _component.Type = "UNION";

                    break;

                case "130":

                    _component.Type = "VALVE";

                    break;

                case "132":

                    _component.Type = "TRAP";

                    break;

                case "134":

                    _component.Type = "SAFETY-DISC";

                    break;

                case "136":

                    _component.Type = "FILTER";

                    break;

                default:

                    stdout.printf("Type unknown - " + _input + "\n");
                    _component.Type = "UNKNOWN";

                    break;
            }

            //* Material Item Code Number *//
            // To find correct material later from array of materials *//
            _component.Material.Number = _item_code_number;

            //* Weight of component *//
            _component.Weight = _weight;

            //* Component Skey *//
            _component.Skey = _skey;

            /* TODO: Setup table with connection points of component
            / to exclude duplicating of points with the same number
             */


            //* Creating Connection Points *//
            // Start point
            Connections.Point? _component_point_1 = new Connections.Point();
                              _component_point_1.Number = 1;
                              _component_point_1.Type = "ARRIVE";
                              _component_point_1.Bore = _pipe_bore;
                              _component_point_1.PosEast = _start_pos_east;
                              _component_point_1.PosNorth = _start_pos_north;
                              _component_point_1.PosElev = _start_pos_elev;

            //End Point
            Connections.Point? _component_point_2 = new Connections.Point();
                              _component_point_2.Number = 2;
                              _component_point_2.Type = "LEAVE";
                              _component_point_2.Bore = _pipe_bore;
                              _component_point_2.PosEast = _end_pos_east;
                              _component_point_2.PosNorth = _end_pos_north;
                              _component_point_2.PosElev = _end_pos_elev;

            // Add points to component connections
            _component.AddConnection( _component_point_1 );
            _component.AddConnection( _component_point_2 );

            return _component;

        }

        //Find Material for Component
        private void ApplyMaterial2Component (Array <Piping.Pipe> _pipes) {
			for (int i = 0; i < _pipes.length; i++) {
				for (int j = 0; j < _pipes.index(i).Components.length; j++){
				    if ( _pipes.index(i).Components.index(j).Material.Number != 0) {
				      	_pipes.index(i).Components.index(j).Material.Code = property_materials.index(_pipes.index(i).Components.index(j).Material.Number - 1 ).Code;
				        _pipes.index(i).Components.index(j).Material.Description = property_materials.index(_pipes.index(i).Components.index(j).Material.Number - 1 ).Description;
				    }
                }
			}
        }

        // Writing MTO report into file
        private void WriteMTOFile (Array <Piping.Pipe> _pipes ) {

            File _mto_file = File.new_for_path (Environment.get_home_dir () + "/Dropbox/VALA/OpenIso/test/MTO.csv");

            try {

                if( _mto_file.query_exists() == true){
                    _mto_file.delete(null);
                }

                FileOutputStream fos = _mto_file.create (FileCreateFlags.REPLACE_DESTINATION, null);
                DataOutputStream dos = new DataOutputStream (fos);

                dos.put_string ( "#;Name;Type;Weight;Skey;Code;Description\n" );
                for (int i = 0; i < _pipes.length; i++) {
				    for (int j = 0; j < _pipes.index(i).Components.length; j++){

                       	dos.put_string ( (i + j + 1 ).to_string() + ";" + _pipes.index(i).Components.index(j).Name + ";" + _pipes.index(i).Components.index(j).Type + ";"  + _pipes.index(i).Components.index(j).Weight.to_string() + ";" + _pipes.index(i).Components.index(j).Skey + ";"  + _pipes.index(i).Components.index(j).Material.Code  + ";" + _pipes.index(i).Components.index(j).Material.Description + "\n"
                       	 );
                    }
			    }

            } catch (Error e) {

                 stderr.printf ("Error: %s\n", e.message);

            }

        }


        private void CollectData () {

            //* Variable for file string *//
            //int  _file_row;

            //* Variable for working string *//
            string  _str_output = "";


            for (int i = 0; i < _file_strings.length  ; i++) {

                int _file_row = int.parse( _file_strings.index (i).substring(0, 5).strip());

                switch (_file_row) {

                    //* Get TextPosisition elements *//
                    case 3:
                        //* Setup current number of text note *//
                        _iCurNoteTextNumber = _iNextNoteTextNumber;

                        //*Add new text note with collected name to text notes array*//
                        //this.property_note_texts.append_val ( new Drawing.Note.Text() );

                        //this.property_note_texts.index ( _iCurNoteTextNumber ).Name = _file_strings.index(i).substring(6,9).strip();

                        //var _text_pos_x = double.parse(_file_strings.index(i).substring(18,8).strip());
                        //var _text_pos_y = double.parse(_file_strings.index(i).substring(24,8).strip());

                        //this.property_note_texts.index ( _iCurNoteTextNumber ).Position = { _text_pos_x, _text_pos_y };

                        //* Increase next number for next loaded text note*//
                        _iNextNoteTextNumber = _iCurNoteTextNumber + 1;

                        break;


                    //* Get name of new pipe *//
                    case -6:
                        //* Setup current number of pipe *//
                        _iCurPipeNumber = _iNextPipeNumber;

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Add new pipe with collected name to Pipes array*//
                        this.Pipes.append_val (new Piping.Pipe ());
                        this.Pipes.index (_iCurPipeNumber).Name = _str_output.to_string();

                        //* Increase next number for future loaded pipe*//
                        _iNextPipeNumber = _iCurPipeNumber + 1;

                        //* Reset components counter for new pipe *//
                        _iCurComponentNumber = 0;
                        _iNextComponentNumber = 0;

                        break;

                    //* Get Pipe Spec *//
                    case -11:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6);

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup pipe spec*//
                        property_pipes.index(_iCurPipeNumber).Spec = _str_output.to_string();

                        break;

                    //* Get Pipe Nominal Pressure Rating *//
                    case -12:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Nominal Pressure Rating of pipe*//
                        property_pipes.index(_iCurPipeNumber).PressureRating = double.parse(_str_output);

                        break;

                    //* Get Pipe Line Type *//
                    case -13:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Nominal Pressure Rating of pipe*//
                        this.property_pipes.index(_iCurPipeNumber).LineType = _str_output;

                        break;

                    //* Get Pipe Insulation Spec Name*//
                    case -15:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Insulation Spec of pipe*//
                        this.property_pipes.index(_iCurPipeNumber).Insulation = _str_output;

                        break;

                    //* Get Pipe Traicing Spec Name*//
                    case -16:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Traicing Spec of pipe*//
                        this.property_pipes.index(_iCurPipeNumber).Tracing = _str_output;

                        break;

                    //* Get Pipe Painting Spec Name*//
                    case -17:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Painting Spec of pipe*//
                        this.property_pipes.index(_iCurPipeNumber).Painting = _str_output;

                        break;

                    //* Get Pipe Temperature*//
                    case -19:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Temperature of pipe*//
                        this.property_pipes.index(_iCurPipeNumber).Temperature = double.parse(_str_output);

                        break;

                    //* Get Material Code*//
                    case -20:

                        //* Setup current number of material *//
                        _iCurMaterialNumber = _iNextMaterialNumber;

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Append new material in material array*//
                        MTO.Material _new_material = new MTO.Material ();
                        property_materials.append_val ( _new_material );
                        property_materials.index ( _iCurMaterialNumber ).Code = _str_output;

                        //* Increase next number for future loaded material*//
                        _iNextMaterialNumber = _iCurMaterialNumber + 1;

                        break;

                    //* Get Material Description*//
                    case -21:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).chomp();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            //* Remove space only right space *//
                            _str_output = _str_output + _file_strings.index (i).substring(6).chomp();
                            //.chomp(
                        }

                        //*Setup Material Description*//
                        property_materials.index(_iCurMaterialNumber).Description = _str_output;

                        break;

                    //* Get Current Component Name *//
                    case -39:

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Name of current component *//
                        property_pipes.index(_iCurPipeNumber).Components.index(_iCurComponentNumber).Name = _str_output;

                        break;

                    default:

                        break;
               }

                //* Condition to define different components *//
                if ( _file_row >= 31 && _file_row <= 137 ) {

                    //* Setup current number of material *//
                    _iCurComponentNumber = _iNextComponentNumber;

                    //* Add new component to current pipe *//
                    property_pipes.index(_iCurPipeNumber).AddComponent ( component_with_properties_from_string( _file_strings.index (i) ) );

                    //* Increase next number for future component in current pipe*//
                    _iNextComponentNumber = _iCurComponentNumber + 1;

                }
            }
        }
    }
}

