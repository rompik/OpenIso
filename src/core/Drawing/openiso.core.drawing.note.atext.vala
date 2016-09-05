using GLib;

namespace OpenIso.Core.Drawing.Shape.Note {
    public class Atext : Object {

        /* Variables */
        private HashTable<int, string?> atextMap = new HashTable<int, string?> (str_hash, str_equal);

        /* Properties */
        /*
         * == Number of Atext ==
         * TODO: Add function to change default text if number is changed
         */
        public int Number { get; set; }

        /*
         * == Text of Atext ==
         */
        public string Text { get; set; }

        /*
        * == Text Size of note ==
        */
        public int Size { get; set; default = 10; }

        /*
         * == Text Font of note ==
         */
        public string Font { get; set; default = "GOST"; }

        /*
         * == Text Font Bold ==
         */
        public bool Bold { get; set; default = false; }

        /*
         * == Text Font Italic ==
         */
        public bool Italic { get; set; default = false; }

        /*
         * == Position of note ==
         */

        public float[] Position { get; set; default = {0, 0}; }

        /*
         * == Horisontal align of note ==
         */

        public string AlignHorizontal { get; set; default = "left"; }

        /*
         * == Vertical align of note ==
         */

        public string AlignVertical { get; set; default = "bottom"; }


        /* Constructor */
        public Atext (int _atextNumber) {

            this.Number = _atextNumber;
            this.Text   = _assign_text_by_value ( this.Number );

        }

        private string _assign_text_by_value (int _atextNumber) {

            atextMap.set(201,"E");
            atextMap.set(202,"N");
            atextMap.set(203,"W");
            atextMap.set(204,"S");
            atextMap.set(205,"EL +");
            atextMap.set(206,"EL -");
            atextMap.set(207,"NS");
            atextMap.set(208,"CONN. TO");
            atextMap.set(209,"CONT. ON");
            atextMap.set(210,"F");
            atextMap.set(211,"G");
            atextMap.set(212,"B");
            atextMap.set(213,"SPINDLE");
            atextMap.set(214,"MM");
            atextMap.set(215,"REDUCING FLANGE");
            atextMap.set(216,"OFFSET");
            atextMap.set(217,"MITRE");
            atextMap.set(218,"LOBSTER");
            atextMap.set(219,"REINFORCED");
            atextMap.set(220,"LEFT LOOSE");
            atextMap.set(221,"FFW");
            atextMap.set(222,"FALL");
            atextMap.set(223,"DEGREES");
            atextMap.set(224,":");
            atextMap.set(225,"%");
            atextMap.set(226,"GRAD");
            atextMap.set(227,"PER M");
            atextMap.set(228,"PER FT");
            atextMap.set(229,"SCREWED END");
            atextMap.set(230,"VENT");
            atextMap.set(231,"BEND");
            atextMap.set(232,"SPEC");
            atextMap.set(233,"C");
            atextMap.set(234,"START");
            atextMap.set(235,"COMMENCE");
            atextMap.set(236,"S");
            atextMap.set(237,"");
            atextMap.set(238,"'");
            atextMap.set(239,"DRAIN");
            atextMap.set(240,"");
            atextMap.set(241,"");
            atextMap.set(242,"");
            atextMap.set(243,"");
            atextMap.set(244,"UP");
            atextMap.set(245,"DOWN");
            atextMap.set(246,"NORTH");
            atextMap.set(247,"SOUTH");
            atextMap.set(248,"EAST");
            atextMap.set(249,"WEST");
            atextMap.set(250,"DATE");
            atextMap.set(251,"PROJECT NO.");
            atextMap.set(252,"BATCH REF");
            atextMap.set(253,"PIPING SPEC");
            atextMap.set(254,"ISS");
            atextMap.set(255,"DRG");
            atextMap.set(256,"OF");
            atextMap.set(257,"SPL");
            atextMap.set(258,"JAN");
            atextMap.set(259,"FEB");
            atextMap.set(260,"MAR");
            atextMap.set(261,"APR");
            atextMap.set(262,"MAY");
            atextMap.set(263,"JUN");
            atextMap.set(264,"JUL");
            atextMap.set(265,"AUG");
            atextMap.set(266,"SEP");
            atextMap.set(267,"OCT");
            atextMap.set(268,"NOV");
            atextMap.set(269,"DEC");
            atextMap.set(270,"THERMAL INSULATION SPEC");
            atextMap.set(271,"TRACING SPEC");
            atextMap.set(272,"PAINTING SPEC");
            atextMap.set(273,"LG");
            atextMap.set(274,"");
            atextMap.set(275,"SWEPT TEE");
            atextMap.set(276,"CONT. FROM");
            atextMap.set(277,"ORIFICE FLANGE");
            atextMap.set(278,"DIAL FACE");
            atextMap.set(279,"L");
            atextMap.set(280,"TAPPING");
            atextMap.set(281,"TAIL");
            atextMap.set(282,"WINDOW");
            atextMap.set(283,"FLAT");
            atextMap.set(284,"TEE BEND");
            atextMap.set(285,"RATING FLANGE");
            atextMap.set(286,"");
            atextMap.set(287,"ORIENTATION DIRECTION");
            atextMap.set(288,"PIPE");
            atextMap.set(289,"MATL");
            atextMap.set(290,"INSUL");
            atextMap.set(291,"TRACE");
            atextMap.set(292,"PAINT");
            atextMap.set(293,"");
            atextMap.set(294,"");
            atextMap.set(295,"");
            atextMap.set(296,"");
            atextMap.set(297,"");
            atextMap.set(298,"TEE ELBOW");
            atextMap.set(299,"COMDACE ITEM CODE DELIMETER");
            atextMap.set(300,"FABRICATION MATERIALS");
            atextMap.set(301,"PT");
            atextMap.set(302,"NO");
            atextMap.set(303,"COMPONENT DESCRIPTION");
            atextMap.set(304,"N.S.");
            atextMap.set(305,"ITEM CODE");
            atextMap.set(306,"QTY");
            atextMap.set(307,"PIPE");
            atextMap.set(308,"FITTINGS");
            atextMap.set(309,"FLANGES");
            atextMap.set(310,"ERECTION MATERIALS");
            atextMap.set(311,"GASKETS");
            atextMap.set(312,"BOLTS");
            atextMap.set(313,"VALVES / INLINE ITEMS");
            atextMap.set(314,"INSTRUMENTS");
            atextMap.set(315,"SUPPORTS");
            atextMap.set(316,"PIPE SPOOLS");
            atextMap.set(317,"PIPE NS");
            atextMap.set(318,"CL LENGTH");
            atextMap.set(319,"CUT PIPE LENGTHS");
            atextMap.set(320,"PIECE");
            atextMap.set(321,"NO");
            atextMap.set(322,"CUT");
            atextMap.set(323,"LENGTH");
            atextMap.set(324,"REMARKS");
            atextMap.set(325,"");
            atextMap.set(326,"PLD BEND");
            atextMap.set(327,"LOOSE FLG");
            atextMap.set(328,"FF WELD");
            atextMap.set(329,"M");
            atextMap.set(330,"INS");
            atextMap.set(331,"MM");
            atextMap.set(332,"PAGE");
            atextMap.set(333,"PIPELINE REF");
            atextMap.set(334,"S");
            atextMap.set(335,"WITH SPECIAL RATING FLANGE(S) (SEE ISO)");
            atextMap.set(336,"SYSTEM REF");
            atextMap.set(337,"D BEND RADIUS");
            atextMap.set(338,"BEND RADIUS");
            atextMap.set(339,"MISCELLANEOUS COMPONENTS");
            atextMap.set(340,"INDUCTION BEND ID ");
            atextMap.set(341,"EQUIPMENT TRIM MATERIALS");
            atextMap.set(342,"NOZZLE REF ");
            atextMap.set(343,"CONTINUED");
            atextMap.set(344,"END CONNECTOR");
            atextMap.set(345,"AND");
            atextMap.set(346,"GEARBOX ORIENTATION");
            atextMap.set(347,"");
            atextMap.set(348,"");
            atextMap.set(349,"PP");
            atextMap.set(350,"REDUCING ELBOW");
            atextMap.set(351,"FABRICATED (PULLED) BEND");
            atextMap.set(352,"WEIGHT");
            atextMap.set(353,"KGS");
            atextMap.set(354,"LBS");
            atextMap.set(355,"TOTAL WEIGHT  THIS DRG");
            atextMap.set(356,"U");
            atextMap.set(357,"B");
            atextMap.set(358,"W");
            atextMap.set(359,"");
            atextMap.set(360,"FT");
            atextMap.set(361,"FTINS");
            atextMap.set(362,"END$ONE");
            atextMap.set(363,"END$TWO");
            atextMap.set(364,"ITEM$CODE");
            atextMap.set(365,"");
            atextMap.set(366,"SQ.CUT");
            atextMap.set(367,"BEVEL");
            atextMap.set(368,"SCREWED");
            atextMap.set(369,"SHAPED");
            atextMap.set(370,"MITRED");
            atextMap.set(371,"OFFSHORE MATERIALS");
            atextMap.set(372,"REMARKS");
            atextMap.set(373,"REM");
            atextMap.set(374,"ANGLE");
            atextMap.set(375,"WELDS");
            atextMap.set(376,"FAB");
            atextMap.set(377,"EREC");
            atextMap.set(378,"OFF");
            atextMap.set(379,"TOTAL FABRICATION WEIGHT");
            atextMap.set(380,"TOTAL ERECTION WEIGHT");
            atextMap.set(381,"TOTAL OFFSHORE WEIGHT");
            atextMap.set(382,"TOTAL WEIGHT UNLISTED ITEMS");
            atextMap.set(383,"*");
            atextMap.set(384,"TANGENT+");
            atextMap.set(385,"CUT/WELD");
            atextMap.set(386,"");
            atextMap.set(387,"");
            atextMap.set(388,"TANGENTIAL CONNECTION");
            atextMap.set(389,"OFFSET CONNECTION");
            atextMap.set(390,"FROM ? ORIGIN");
            atextMap.set(391,"");
            atextMap.set(400,"TRACED PIPE");
            atextMap.set(401,"LAGGED PIPE");
            atextMap.set(402,"PIPE SUPPORT");
            atextMap.set(403,"COMPN JOINT");
            atextMap.set(404,"SCREWED JOINT");
            atextMap.set(405,"SOCKET WELD");
            atextMap.set(406,"FIELD WELD");
            atextMap.set(407,"SHOP WELD");
            atextMap.set(408,"");
            atextMap.set(409,"");
            atextMap.set(410,"");
            atextMap.set(411,"SITE CONNECTION");
            atextMap.set(412,"WELD|SHOP|WELD|WELDER|VISUAL|NDT|HARD|S.R|FAB.QA");
            atextMap.set(413,"NO |/FLD|PROC|   ID   |ACCEPT|NO | NO |     |ACCEPT");
            atextMap.set(414,"S");
            atextMap.set(415,"F");
            atextMap.set(416,"O");
            atextMap.set(417,"BW");
            atextMap.set(418,"SW");
            atextMap.set(419,"MW");
            atextMap.set(420,"LUG");
            atextMap.set(421,"SOF");
            atextMap.set(422,"SOB");
            atextMap.set(423,"LET");
            atextMap.set(450,"B.O.P.");
            atextMap.set(451,"TAPPING CONNECTION");
            atextMap.set(452,"UNACCEPTABLE SPLIT");
            atextMap.set(453,"MM");
            atextMap.set(454,"CONNECTION ORIENTATION");
            atextMap.set(455,"");
            atextMap.set(456,"SEE DETAIL ?");
            atextMap.set(457,"MITRE ?");
            atextMap.set(458,"Default is blank  used for metric bore units");
            atextMap.set(459,"? THK");
            atextMap.set(460,"BEAM$?");
            atextMap.set(461,"COLUMN$?");
            atextMap.set(462,"?$BUILDING CL");
            atextMap.set(463,"CL EQUIPMENT$?");
            atextMap.set(464,"CL PIPELINE$?");
            atextMap.set(465,"?$FLOOR LEVEL");
            atextMap.set(466,"?$WALL");
            atextMap.set(467,"GRID LINE$?");
            atextMap.set(468,"");
            atextMap.set(469,"REFERENCE POINT");
            atextMap.set(470,"SUPPORT LOCATION");
            atextMap.set(471,"LOCATIONPOINT?");
            atextMap.set(472,"NO.?");
            atextMap.set(473,"OF");
            atextMap.set(474,"ABOVE");
            atextMap.set(475,"");
            atextMap.set(476,"");
            atextMap.set(477,"CUT OUT ?");
            atextMap.set(478,"J");
            atextMap.set(481,"E");
            atextMap.set(482,"N");
            atextMap.set(483,"W");
            atextMap.set(484,"S");
            atextMap.set(485,"U");
            atextMap.set(486,"D");
            atextMap.set(487,"*** REFERENCE FLAT ***");
            atextMap.set(488,"*** REFERENCE SPINDLE ***");
            atextMap.set(489,"*** REFERENCE SUPPORT ***");
            atextMap.set(490,"*** REFERENCE BRANCH ***");
            atextMap.set(491,"*** REFERENCE WINDOW ***");
            atextMap.set(492,"FLAT DIRECTION");
            atextMap.set(493,"SPINDLE DIRECTION");
            atextMap.set(494,"SUPPORT DIRECTION");
            atextMap.set(495,"BRANCH DIRECTION");
            atextMap.set(496,"WINDOW DIRECTION");
            atextMap.set(497,"FLANGE ROTATION ?");
            atextMap.set(498,"Default is blank  SITE WELD");
            atextMap.set(499,"SHOP TEST WELD");
            atextMap.set(500,"SHOP TEST");
            atextMap.set(501,"");
            atextMap.set(502,"SUPPORT");
            atextMap.set(503,"SPOOL ID");
            atextMap.set(504,"");
            atextMap.set(507,"RPD");
            atextMap.set(508,"LF");
            atextMap.set(509,"L4");
            atextMap.set(510,"");
            atextMap.set(511,"PAD");
            atextMap.set(512,"TACK WELD");
            atextMap.set(513,"TW");
            atextMap.set(514,"REINFPAD");
            atextMap.set(515,"REINFORCEMENT PAD FOR@");
            atextMap.set(516,"TRN");
            atextMap.set(517,"5");
            atextMap.set(518,"1");
            atextMap.set(519,"EB");
            atextMap.set(520,"RL");
            atextMap.set(521,"FW");
            atextMap.set(522,"");
            atextMap.set(523,"");
            atextMap.set(524,"");
            atextMap.set(525,"");
            atextMap.set(526,"");
            atextMap.set(527,"");
            atextMap.set(528,"");
            atextMap.set(529,"");
            atextMap.set(530,"");
            atextMap.set(531,"");
            atextMap.set(532,"");
            atextMap.set(533,"FI");
            atextMap.set(534,"RL");
            atextMap.set(535,"SU");
            atextMap.set(536,"VL");
            atextMap.set(537,"");
            atextMap.set(538,"");
            atextMap.set(539,",");
            atextMap.set(540,"");
            atextMap.set(541,"N");
            atextMap.set(542,"S");
            atextMap.set(543,"");
            atextMap.set(544,"");
            atextMap.set(545,"/");

            return atextMap[_atextNumber];

        }
    }
}
