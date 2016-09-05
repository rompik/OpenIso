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
        //private File _File = null;
        //private int i = 0;
        //private string[] _FileStrings = null;


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


        //*Map for storing Types of components*//
        //private HashMap<int, string> mapComponentTypes = new HashMap<int, string> ();

        //*Collection of imported notes*//
        //private Array <string> property_notes = new Array <string> ();
        private Array <Drawing.Note.Text> property_note_texts = new Array<Drawing.Note.Text> ();
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

                stdout.printf( "\n");


                CollectData ();



                ApplyMaterial2Component (this.Pipes);

            }

            catch (Error e) {
                error ("%s", e.message);
            }

        }

        // Method to get properties of component from string
        private Array <string> component_properties_from_string (string _input) {

            var _output = new Array <string> ();

            //* (0) - Start Position East / West *//
            _output.append_val ( _input.substring(6,11).strip() );

            //* (1) - Start Position North / South *//
            _output.append_val ( _input.substring(17,10).strip() );

            //* (2) - Start Position Eleveation +/- *//
            _output.append_val ( _input.substring(27,10).strip() );

            //* (3) - End Position East / West *//
            _output.append_val ( _input.substring(37,12).strip() );

            //* (4) - End Position North / South *//
            _output.append_val ( _input.substring(49,10).strip() );

            //* (5) - End Position Eleveation +/- *//
            _output.append_val ( _input.substring(59,10).strip() );

            //* (6) - Pipe Bore *//
            _output.append_val ( _input.substring(69,8).strip() );

            //* (7) - Item Code *//
            _output.append_val ( _input.substring(76,10).strip() );

            //* (8) - Component Weight *//
            _output.append_val ( _input.substring(87,8).strip() );

            //* (9) - *//
            _output.append_val ( _input.substring(69,8).strip() );

            //* (10) - Skey Code *//
            _output.append_val ( _input.substring(104,4).strip() );

            //* (11) - *//
            _output.append_val ( _input.substring(69,8).strip() );

            return _output;

        }

        //Find Material for Component
        private void ApplyMaterial2Component (Array <Piping.Pipe> _pipes) {
			for (int i = 0; i < _pipes.length; i++) {
				for (int j = 0; j < _pipes.index(i).Components.length; j++){
                   	//_pipes.index(i).Components.index(j).Material = property_materials.index(j);
                }
			}

			WriteMTOFile (_pipes);
        }

        private void WriteMTOFile (Array <Piping.Pipe> _pipes ) {

            File _mto_file = File.new_for_path (Environment.get_home_dir () + "/Dropbox/VALA/openiso/test/MTO.txt");

            try {

                if( _mto_file.query_exists() == true){
                    _mto_file.delete(null);
                }

                FileOutputStream fos = _mto_file.create (FileCreateFlags.REPLACE_DESTINATION, null);
                DataOutputStream dos = new DataOutputStream (fos);

                for (int i = 0; i < property_materials.length; i++) {
                    stdout.printf(property_materials.index(i).Code + "\n");
                    stdout.printf(property_materials.index(i).Description + "\n");
                }

                for (int i = 0; i < _pipes.length; i++) {
				    for (int j = 0; j < _pipes.index(i).Components.length; j++){
				        dos.put_string ( "Component\n" );
                       	dos.put_string ( "  Type - " + _pipes.index(i).Components.index(j).Type + "\n" );
                       	dos.put_string ( "  Code - " + _pipes.index(i).Components.index(j).Material.Code + "\n" );
                       	dos.put_string ( "  Description - " + _pipes.index(i).Components.index(j).Material.Description + "\n" );
                    }
			    }

            } catch (Error e) {

                 stderr.printf ("Error: %s\n", e.message);

            }

        }

        private void CollectData () {

            string  _file_row = "";
            string  _str_output = "";
            //string  _component_type = "";
            double  _component_p1_bore = 0;
            double  _component_p2_bore = 0;
            //double  _component_p3_bore = 0;
            //double  _component_length = 0;
            //int     _component_quantity = 0;
            //string  _component_marker = null;
            //string  _component_part_number = null;

            for (int i = 0; i < _file_strings.length  ; i++) {
                _file_row = _file_strings.index (i).substring(0, 5).strip();

                switch (_file_row) {

                    //* Get TextPosisition elements *//
                    case "3":
                        //* Setup current number of text note *//
                        _iCurNoteTextNumber = _iNextNoteTextNumber;

                        //*Add new text note with collected name to text notes array*//
                        this.property_note_texts.append_val ( new Drawing.Note.Text() );

                        //this.property_note_texts.index ( _iCurNoteTextNumber ).Name = _file_strings.index(i).substring(6,9).strip();

                        //var _text_pos_x = double.parse(_file_strings.index(i).substring(18,8).strip());
                        //var _text_pos_y = double.parse(_file_strings.index(i).substring(24,8).strip());

                        //this.property_note_texts.index ( _iCurNoteTextNumber ).Position = { _text_pos_x, _text_pos_y };

                        //* Increase next number for next loaded text note*//
                        _iNextNoteTextNumber = _iCurNoteTextNumber + 1;

                        break;


                    //* Get name of new pipe *//
                    case "-6":
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
                    case "-11":

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
                    case "-12":

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
                    case "-13":

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
                    case "-15":

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
                    case "-16":

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
                    case "-17":

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
                    case "-19":

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
                    case "-20":

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
                        var _new_material = new MTO.Material ();
                        property_materials.append_val (_new_material);
                        property_materials.index ( _iCurMaterialNumber ).Code = _str_output;

                        //* Increase next number for future loaded material*//
                        _iNextMaterialNumber = _iCurMaterialNumber + 1;

                        stdout.printf("Materials Number" + property_materials.length.to_string() + "\n" );

                        break;

                    //* Get Material Description*//
                    case "-21":

                        //*Collect value of string and remove spaces*//
                        _str_output = _file_strings.index (i).substring(6).strip();

                        //* Read next strings if current string can be long *//
                        while (_file_strings.index (i + 1).substring(0, 5) == "   -1") {
                            i = i + 1;
                            _str_output = _str_output + _file_strings.index (i).substring(6).strip();
                        }

                        //*Setup Material Description*//
                        property_materials.index(_iCurMaterialNumber).Description = _str_output;


                        break;

                    //* Get new ELBOW in current pipe*//
                    case "35":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */

                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");

                        _component_p1_bore = double.parse( component_properties_from_string ( _file_strings.index (i) ).index(6) );
                        _component_p2_bore = double.parse( component_properties_from_string ( _file_strings.index (i) ).index(6) );


                        //*Add new component with required type for current pipe*//
                        var _new_elbow = new Piping.Component();
                            _new_elbow.Name = _iCurComponentNumber.to_string();
                            _new_elbow.Type = "ELBOW";
                            _new_elbow.Skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new Connections.Point(1);
                            _new_elbow.AddConnection(_new_point_1);

                        var _new_point_2 = new Connections.Point(2);
                            _new_elbow.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_elbow );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;

                    //* Get new TEE in current pipe*//
                    case "45":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */
                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");

                        _component_p1_bore = double.parse( component_properties_from_string ( _file_strings.index (i) ).index(6) );
                        _component_p2_bore = double.parse( component_properties_from_string ( _file_strings.index (i) ).index(6) );


                        //*Add new component with required type for current pipe*//
                        var _new_tee = new Piping.Component();
                            _new_tee.Name = _iCurComponentNumber.to_string();
                            _new_tee.Type = "TEE";
                            _new_tee.Skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new Connections.Point(1);
                            _new_tee.AddConnection(_new_point_1);

                        var _new_point_2 = new Connections.Point(2);
                            _new_tee.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_tee );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;


                    //* Get new REDUCER in current pipe*//
                    case "55":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */
                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");

                        _component_p1_bore = double.parse( _pipe_bore );
                        _component_p2_bore = double.parse( _pipe_bore );


                        //*Add new component with required type for current pipe*//
                        var _new_reducer = new OpenIso.Core.Piping.Component();
                            _new_reducer.Name = _iCurComponentNumber.to_string();
                            _new_reducer.Type = "REDUCER";
                            _new_reducer.Skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new OpenIso.Core.Connections.Point(1);
                            _new_reducer.AddConnection(_new_point_1);

                        var _new_point_2 = new OpenIso.Core.Connections.Point(2);
                            _new_reducer.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_reducer );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;

                    //* Get new TUBE in current pipe*//
                    case "100":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */
                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");


                        _component_p1_bore = double.parse( _pipe_bore );
                        _component_p2_bore = double.parse( _pipe_bore );


                        //*Add new component with required type for current pipe*//
                        var _new_tube = new OpenIso.Core.Piping.Component();
                            _new_tube.Name = _iCurComponentNumber.to_string();
                            _new_tube.Type = "TUBE";
                            _new_tube.Skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new OpenIso.Core.Connections.Point(1);
                            _new_tube.AddConnection(_new_point_1);

                        var _new_point_2 = new OpenIso.Core.Connections.Point(2);
                            _new_tube.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_tube );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;

                    //* Get new Flange in current pipe*//
                    case "105":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */
                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");

                        _component_p1_bore = double.parse( _pipe_bore );
                        _component_p2_bore = double.parse( _pipe_bore );


                        //*Add new component with required type for current pipe*//
                        var _new_flange = new OpenIso.Core.Piping.Component();
                            _new_flange.Name = _iCurComponentNumber.to_string();
                            _new_flange.Type = "FLANGE";
                            _new_flange.Skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new OpenIso.Core.Connections.Point(1);
                            _new_flange.AddConnection(_new_point_1);

                        var _new_point_2 = new OpenIso.Core.Connections.Point(2);
                            _new_flange.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_flange );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;

                    //* Get new Gasket in current pipe*//
                    case "110":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */
                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");

                        _component_p1_bore = double.parse( _pipe_bore );
                        _component_p2_bore = double.parse( _pipe_bore );

                        //*Add new component with required type for current pipe*//
                        var _new_gasket = new OpenIso.Core.Piping.Component();
                            _new_gasket.Name = _iCurComponentNumber.to_string();
                            _new_gasket.Type = "GASKET";
                            _new_gasket.Skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new OpenIso.Core.Connections.Point(1);
                            _new_gasket.AddConnection(_new_point_1);

                        var _new_point_2 = new OpenIso.Core.Connections.Point(2);
                            _new_gasket.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_gasket );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;

                    //* Get new Bolt in current pipe*//
                    case "115":

                        //* Setup current number of material *//
                        _iCurComponentNumber = _iNextComponentNumber;

                        //*Collect values from string and remove spaces*//
                        /* TODO:
                         * 1) Define size of array
                         * 2) Define last member index
                         * 3) Add Map for Number -> Component Type
                         */
                        var _pos_start_east = component_properties_from_string ( _file_strings.index (i) ).index(0);
                        var _pos_start_north = component_properties_from_string ( _file_strings.index (i) ).index(1);
                        var _pos_start_elev = component_properties_from_string ( _file_strings.index (i) ).index(2);
                        var _pos_end_east = component_properties_from_string ( _file_strings.index (i) ).index(3);
                        var _pos_end_north = component_properties_from_string ( _file_strings.index (i) ).index(4);
                        var _pos_end_elev = component_properties_from_string ( _file_strings.index (i) ).index(5);
                        var _pipe_bore = component_properties_from_string ( _file_strings.index (i) ).index(6);
                        var _item_code = component_properties_from_string ( _file_strings.index (i) ).index(7);
                        var _comp_weight = component_properties_from_string ( _file_strings.index (i) ).index(8);
                        var _dummy = component_properties_from_string ( _file_strings.index (i) ).index(9);
                        var _comp_skey = component_properties_from_string ( _file_strings.index (i) ).index(10);

                        //stdout.printf(_file_strings.index (i) + "\n");
                        //stdout.printf("Component Pos Start East -  " + _pos_start_east + "\n");
                        //stdout.printf("Component Pos Start North - " + _pos_start_north + "\n");
                        //stdout.printf("Component Pos Start Up -    " + _pos_start_elev + "\n");
                        //stdout.printf("Component Pos End East -    " + _pos_end_east + "\n");
                        //stdout.printf("Component Pos End North -   " + _pos_end_north + "\n");
                        //stdout.printf("Component Pos End Up -      " + _pos_end_elev + "\n");
                        //stdout.printf("Component Item Code -       " + _item_code + "\n");
                        //stdout.printf("Component Skey -            " + _comp_skey + "\n");
                        //stdout.printf("Component Weight -          " + _comp_weight + "\n");
                        //stdout.printf("Component Pipe Bore -       " + _pipe_bore + "\n");
                        //stdout.printf("Component Dummy -           " + _dummy + "\n");

                        _component_p1_bore = double.parse( _pipe_bore );
                        _component_p2_bore = double.parse( _pipe_bore );


                        //*Add new component with required type for current pipe*//
                        var _new_pipe_bolt = new OpenIso.Core.Piping.Component();
                            _new_pipe_bolt.Name = _iCurComponentNumber.to_string();
                            _new_pipe_bolt.Type = "BOLT";

                        //*Setup connection Points of component*//
                        //*TODO: Fix problem with new Point*//
                        var _new_point_1 = new OpenIso.Core.Connections.Point(1);
                            _new_pipe_bolt.AddConnection(_new_point_1);

                        var _new_point_2 = new OpenIso.Core.Connections.Point(2);
                            _new_pipe_bolt.AddConnection(_new_point_2);

                        //*TODO: Add new components*//
                        //property_pipes.index(_iCurPipeNumber).Components;
                        property_pipes.index(_iCurPipeNumber).AddComponent ( _new_pipe_bolt );

                        //* Increase next number for future component in current pipe*//
                        _iNextComponentNumber = _iCurComponentNumber + 1;

                        break;



                    default:

                        break;

                }

                //Clear string after apply new value
                _str_output = "";

            }

        }
    }
}

