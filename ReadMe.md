# Sylvr Chatbot

A modern chatbot application with voice input/output capabilities, built with Next.js, FastAPI, and MongoDB.

## Features

- Real-time chat interface with WebSocket connection
- Voice input with automatic transcription using Whisper
- Text-to-speech output using Google TTS
- MongoDB integration for data storage
- Modern UI with dark mode

## Prerequisites

- Python 3.11
- Node.js 18+ and npm
- MongoDB instance (local or cloud)

## Setup Instructions

### Backend Setup

1. Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your MongoDB connection string:
```
MONGODB_URL=your_mongodb_connection_string
```

4. Start the backend server:
```bash
# Start the main FastAPI server with WebSocket support
uvicorn chatbot.main:app --host 0.0.0.0 --port 8000

# In a separate terminal, start the TTS server
uvicorn TTS:app --host 0.0.0.0 --port 8001
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
.
├── chatbot/             # Backend chatbot implementation
│   └── main.py         # Main FastAPI application with WebSocket
├── frontend/           # Next.js frontend application
│   ├── app/           # Next.js app directory
│   ├── components/    # React components
│   └── public/        # Static assets
├── TTS.py             # Text-to-speech and transcription service
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Usage

1. Open the application in your browser at `http://localhost:3000`
2. Type messages in the input box or use the microphone button to record voice input
3. Click the speaker icon next to bot responses to hear them spoken aloud
4. The chat interface supports both text and voice interactions

## Development

- The frontend is built with Next.js and uses Tailwind CSS for styling
- The backend uses FastAPI for both REST API and WebSocket endpoints
- Voice transcription is handled by OpenAI's Whisper model
- Text-to-speech is implemented using Google's TTS service

## Notes

- Make sure both backend servers (main and TTS) are running for full functionality
- The microphone feature requires browser permissions
- For production deployment, update the CORS settings in TTS.py with your frontend URL


examples:

query: List all customers with active benefits
"summary": "Here is a list of customers who have at least one active benefit. The query result includes each customer's username, full name, address, birthdate, email address, and associated account numbers.\n\n```json\n[\n  {\n    \"username\": \"odonovan\",\n    \"name\": \"Edward Owen\",\n    \"address\": \"404 Acosta Alley\\nHicksland, MN 94828\",\n    \"birthdate\": \"1971-01-11T18:59:31\",\n    \"email\": \"stokessharon@yahoo.com\",\n    \"accounts\": [\n      999198,\n      614528,\n      421981,\n      545935,\n      872805\n    ]\n  },\n  {\n    \"username\": \"angelathomas\",\n    \"name\": \"Shane Mills\",\n    \"address\": \"73703 Brandon Dale\\nCastilloview, TN 40641\",\n    \"birthdate\": \"1980-10-29T09:03:06\",\n    \"email\": \"lmartinez@hotmail.com\",\n    \"accounts\": [\n      214555,\n      201862,\n      720825\n    ]\n  },\n  {\n    \"username\": \"psnow\",\n    \"name\": \"Kelly Clark\",\n    \"address\": \"4596 April Cove Apt. 056\\nAllenville, LA 48741\",\n    \"birthdate\": \"1996-03-14T23:23:36\",\n    \"email\": \"davidsullivan@hotmail.com\",\n    \"accounts\": [\n      741232\n    ]\n  },\n  {\n    \"username\": \"bakerandre\",\n    \"name\": \"Michelle Jones\",\n    \"address\": \"76197 Mary Turnpike\\nPort Susanshire, ME 03093\",\n    \"birthdate\": \"1972-12-03T18:54:38\",\n    \"email\": \"natasha35@hotmail.com\",\n    \"accounts\": [\n      181212\n    ]\n  },\n  {\n    \"username\": \"durankatie\",\n    \"name\": \"Joshua Daniels\",\n    \"address\": \"308 Nathaniel Row\\nDicksonstad, MD 14577\",\n    \"birthdate\": \"1985-10-12T10:00:27\",\n    \"email\": \"mcdowelldaniel@hotmail.com\",\n    \"accounts\": [\n      426335,\n      308785,\n      541517,\n      451481,\n      906290\n    ]\n  },\n  {\n    \"username\": \"awilliams\",\n    \"name\": \"Linda Lee\",\n    \"address\": \"018 David Extension\\nLeblancchester, TX 96335\",\n    \"birthdate\": \"1991-03-05T11:18:06\",\n    \"email\": \"morrisondavid@gmail.com\",\n    \"accounts\": [\n      273420\n    ]\n  },\n  {\n    \"username\": \"weaverlarry\",\n    \"name\": \"Jonathan Strong\",\n    \"address\": \"398 Carpenter Park\\nBakerfurt, MT 74208\",\n    \"birthdate\": \"1985-07-09T18:01:22\",\n    \"email\": \"hansonmichael@gmail.com\",\n    \"accounts\": [\n      540341,\n      363138,\n      495198,\n      616103\n    ]\n  },\n  {\n    \"username\": \"keith63\",\n    \"name\": \"James Martin\",\n    \"address\": \"71056 Hardin Vista Suite 883\\nPort William, NC 37618\",\n    \"birthdate\": \"1986-10-24T06:41:21\",\n    \"email\": \"michael75@yahoo.com\",\n    \"accounts\": [\n      62713,\n      278149,\n      298562,\n      51474\n    ]\n  },\n  {\n    \"username\": \"nicholas29\",\n    \"name\": \"Robert Reynolds MD\",\n    \"address\": \"42662 Nicholas Lane Apt. 050\\nPort Joshuafurt, WV 05961\",\n    \"birthdate\": \"1970-08-06T07:36:20\",\n    \"email\": \"jkhan@hotmail.com\",\n    \"accounts\": [\n      996752\n    ]\n  },\n  {\n    \"username\": \"sharon50\",\n    \"name\": \"Dennis Brown\",\n    \"address\": \"USS Petersen\\nFPO AA 41929\",\n    \"birthdate\": \"1997-02-16T18:03:39\",\n    \"email\": \"dawn26@hotmail.com\",\n    \"accounts\": [\n      111213,\n      722342,\n      162819,\n      662854,\n      118623,\n      95826\n    ]\n  },\n  {\n    \"username\": \"billy76\",\n    \"name\": \"Samuel Mcintosh\",\n    \"address\": \"USS Rice\\nFPO AP 26057\",\n    \"birthdate\": \"1992-06-24T06:36:27\",\n    \"email\": \"masonkaren@yahoo.com\",\n    \"accounts\": [\n      669029,\n      847533,\n      727330,\n      729752,\n      882334,\n      369055\n    ]\n  },\n  {\n    \"username\": \"hpatrick\",\n    \"name\": \"Mrs. Sara Maxwell\",\n    \"address\": \"468 Fuller Harbors\\nMarilynshire, DC 97762\",\n    \"birthdate\": \"1980-04-30T19:31:19\",\n    \"email\": \"rgordon@yahoo.com\",\n    \"accounts\": [\n      129343,\n      744624,\n      303388,\n      711252,\n      928506,\n      265264\n    ]\n  },\n  {\n    \"username\": \"karenfarrell\",\n    \"name\": \"Charles Flores\",\n    \"address\": \"63432 Morton Mills\\nAlexischester, MA 22487\",\n    \"birthdate\": \"1972-02-02T09:42:02\",\n    \"email\": \"rebecca51@hotmail.com\",\n    \"accounts\": [\n      558623,\n      262488\n    ]\n  },\n  {\n    \"username\": \"suzanne81\",\n    \"name\": \"Belinda Khan\",\n    \"address\": \"2207 Walters Camp Apt. 682\\nSouth Sabrinamouth, MS 61646\",\n    \"birthdate\": \"1985-06-14T16:42:48\",\n    \"email\": \"sherry31@yahoo.com\",\n    \"accounts\": [\n      436662,\n      791099,\n      906770,\n      375486,\n      299822,\n      469791\n    ]\n  },\n  {\n    \"username\": \"nicole25\",\n    \"name\": \"Jeremy Sullivan\",\n    \"address\": \"944 Gilbert Haven Suite 424\\nEthanmouth, MI 48995\",\n    \"birthdate\": \"1992-12-19T04:38:59\",\n    \"email\": \"jacob15@hotmail.com\",\n    \"accounts\": [\n      851226,\n      998674,\n      577795\n    ]\n  },\n  {\n    \"username\": \"petergilbert\",\n    \"name\": \"Angela Campbell\",\n    \"address\": \"4068 Espinoza Mills\\nWest Jessica, WV 60790\",\n    \"birthdate\": \"1991-12-15T18:03:16\",\n    \"email\": \"jocelyn67@yahoo.com\",\n    \"accounts\": [\n      260499,\n      946116,\n      588389,\n      293111,\n      126444,\n      678107\n    ]\n  },\n  {\n    \"username\": \"santosjordan\",\n    \"name\": \"Gabriel Meza\",\n    \"address\": \"1691 Soto Villages Apt. 217\\nLake Robertmouth, NJ 48815\",\n    \"birthdate\": \"1986-03-05T06:55:04\",\n    \"email\": \"nancywhite@hotmail.com\",\n    \"accounts\": [\n      397600,\n      455692\n    ]\n  },\n  {\n    \"username\": \"gonzalesgabriel\",\n    \"name\": \"Michael Harris\",\n    \"address\": \"74982 Jasmine Trace\\nYoungfort, AZ 36102\",\n    \"birthdate\": \"1980-12-17T05:07:38\",\n    \"email\": \"aarongreer@hotmail.com\",\n    \"accounts\": [\n      569388,\n      816560,\n      328686\n    ]\n  },\n  {\n    \"username\": \"carrollanita\",\n    \"name\": \"Andrew Reilly\",\n    \"address\": \"7335 Mcmillan Port Suite 707\\nWest Kristine, NE 13112\",\n    \"birthdate\": \"1989-07-11T14:00:48\",\n    \"email\": \"johnharris@hotmail.com\",\n    \"accounts\": [\n      942656\n    ]\n  },\n  {\n    \"username\": \"nicholassmith\",\n    \"name\": \"Amy Lawrence\",\n    \"address\": \"76259 Smith Common\\nMadisonland, IN 48787\",\n    \"birthdate\": \"1989-06-14T09:13:05\",\n    \"email\": \"christophercastro@hotmail.com\",\n    \"accounts\": [\n      640540,\n      303463,\n      981415,\n      633630\n    ]\n  },\n  {\n    \"username\": \"campbellalicia\",\n    \"name\": \"Wesley Rodriguez\",\n    \"address\": \"9230 Christine Court\\nNorth Manuel, WA 20784\",\n    \"birthdate\": \"1969-12-20T00:38:18\",\n    \"email\": \"fergusonshane@gmail.com\",\n    \"accounts\": [\n      745392,\n      385319\n    ]\n  },\n  {\n    \"username\": \"tinajacobs\",\n    \"name\": \"Marie Torres\",\n    \"address\": \"844 Weaver Turnpike Apt. 338\\nSouth Robertton, AL 13154\",\n    \"birthdate\": \"1987-06-03T19:26:40\",\n    \"email\": \"mcintoshalbert@yahoo.com\",\n    \"accounts\": [\n      785218,\n      155366,\n      379691,\n      386231\n    ]\n  },\n  {\n    \"username\": \"lejoshua\",\n    \"name\": \"Michael Johnson\",\n    \"address\": \"15989 Edward Inlet\\nLake Maryton, NC 39545\",\n    \"birthdate\": \"1971-09-23T02:01:15\",\n    \"email\": \"courtneypaul@gmail.com\",\n    \"accounts\": [\n      470650,\n      443178\n    ]\n  },\n  {\n    \"username\": \"ogreen\",\n    \"name\": \"Jose Lucas\",\n    \"address\": \"95550 Makayla Lodge Apt. 078\\nMasseymouth, IN 35955\",\n    \"birthdate\": \"1974-03-31T13:45:46\",\n    \"email\": \"zyoung@gmail.com\",\n    \"accounts\": [\n      87286,\n      886274,\n      569434\n    ]\n  },\n  {\n    \"username\": \"ianjones\",\n    \"name\": \"Douglas Johnson\",\n    \"address\": \"8909 Cummings Streets Apt. 479\\nEast Julie, DE 32862\",\n    \"birthdate\": \"1979-11-30T10:36:54\",\n    \"email\": \"bennettwendy@yahoo.com\",\n    \"accounts\": [\n      866159,\n      950569,\n      871955,\n      391838,\n      129238,\n      280867\n    ]\n  },\n  {\n    \"username\": \"michael24\",\n    \"name\": \"Terry Nicholson\",\n    \"address\": \"08337 Houston Plain Suite 594\\nSouth Bradley, NC 51711\",\n    \"birthdate\": \"1988-04-01T05:53:22\",\n    \"email\": \"sanchezalex@yahoo.com\",\n    \"accounts\": [\n      620350,\n      797297,\n      352008,\n      360322,\n      913332,\n      373260\n    ]\n  },\n  {\n    \"username\": \"icooke\",\n    \"name\": \"Julie Mora\",\n    \"address\": \"3605 Matthews Fork Apt. 419\\nSouth Carolynmouth, VT 62295\",\n    \"birthdate\": \"1982-03-06T19:47:54\",\n    \"email\": \"clarkjean@gmail.com\",\n    \"accounts\": [\n      898675,\n      264514,\n      856800\n    ]\n  },\n  {\n    \"username\": \"atorres\",\n    \"name\": \"Amber Collier\",\n    \"address\": \"583 Brittany Walk Suite 856\\nDuncanside, NH 33546\",\n    \"birthdate\": \"1988-04-22T14:09:30\",\n    \"email\": \"mia28@yahoo.com\",\n    \"accounts\": [\n      686986,\n      965131,\n      143720,\n      475571,\n      856354\n    ]\n  },\n  {\n    \"username\": \"christophercooper\",\n    \"name\": \"Denise Curtis\",\n    \"address\": \"942 Jennifer Forest\\nWatkinsburgh, MI 96943\",\n    \"birthdate\": \"1975-03-06T20:46:53\",\n    \"email\": \"fmoore@hotmail.com\",\n    \"accounts\": [\n      385025,\n      412109,\n      201161\n    ]\n  },\n  {\n    \"username\": \"laurapatterson\",\n    \"name\": \"Ms. Kristen Williams MD\",\n    \"address\": \"76047 Stevens View Suite 495\\nToddside, NM 83256\",\n    \"birthdate\": \"1986-08-11T16:14:57\",\n    \"email\": \"stephenwarner@hotmail.com\",\n    \"accounts\": [\n      964509,\n      323481\n    ]\n  },\n  {\n    \"username\": \"nataliebrooks\",\n    \"name\": \"Matthew Medina\",\n    \"address\": \"57893 Mathews Rest Apt. 316\\nGrantshire, VA 94216\",\n    \"birthdate\": \"1980-06-02T23:11:50\",\n    \"email\": \"tina96@hotmail.com\",\n    \"accounts\": [\n      246018,\n      591354,\n      182094,\n      565145,\n      895434\n    ]\n  },\n  {\n    \"username\": \"walkerashley\",\n    \"name\": \"Marc Cain\",\n    \"address\": \"39716 Sims Stravenue Apt. 559\\nSloanland, DC 92306\",\n    \"birthdate\": \"1997-04-11T06:31:30\",\n    \"email\": \"kennethrodgers@gmail.com\",\n    \"accounts\": [\n      980440,\n      626807,\n      313907,\n      218101,\n      157495,\n      736396\n    ]\n  },\n  {\n    \"username\": \"derek98\",\n    \"name\": \"Sandra Davila\",\n    \"address\": \"599 Joshua Shore\\nEast Nancymouth, MD 39549\",\n    \"birthdate\": \"1972-10-07T10:25:14\",\n    \"email\": \"rgraham@hotmail.com\",\n    \"accounts\": [\n      795756,\n      903651,\n      149247,\n      133163,\n      652071,\n      921410\n    ]\n  },\n  {\n    \"username\": \"david77\",\n    \"name\": \"Aaron Perez\",\n    \"address\": \"55375 Malone Trail Suite 506\\nSouth Miguelland, MS 55765\",\n    \"birthdate\": \"1982-08-07T02:49:55\",\n    \"email\": \"alexaortega@hotmail.com\",\n    \"accounts\": [\n      744220,\n      126092,\n      187107,\n      437371,\n      413293\n    ]\n  },\n  {\n    \"username\": \"brenda56\",\n    \"name\": \"Austin Johnson\",\n    \"address\": \"165 Brittany Green\\nNorth Eric, MN 84627\",\n    \"birthdate\": \"1971-06-12T23:52:56\",\n    \"email\": \"mcguirejennifer@yahoo.com\",\n    \"accounts\": [\n      248380,\n      244782\n    ]\n  },\n  {\n    \"username\": \"brownbrian\",\n    \"name\": \"Michele Mitchell\",\n    \"address\": \"631 Donna Forges\\nSouth John, OK 12233\",\n    \"birthdate\": \"1984-09-13T14:22:01\",\n    \"email\": \"juanmalone@gmail.com\",\n    \"accounts\": [\n      962477,\n      505367\n    ]\n  },\n  {\n    \"username\": \"patrick05\",\n    \"name\": \"Curtis Walter\",\n    \"address\": \"42614 Hartman Drive Suite 169\\nYangside, NC 31349\",\n    \"birthdate\": \"1972-12-03T02:28:33\",\n    \"email\": \"jevans@yahoo.com\",\n    \"accounts\": [\n      59378,\n      181687,\n      448304,\n      754737,\n      176390\n    ]\n  },\n  {\n    \"username\": \"caroline49\",\n    \"name\": \"Jennifer Carter\",\n    \"address\": \"720 Miller Circle\\nParkschester, NM 03319\",\n    \"birthdate\": \"1992-01-05T03:01:14\",\n    \"email\": \"hatfieldcurtis@yahoo.com\",\n    \"accounts\": [\n      881765,\n      76339\n    ]\n  },\n  {\n    \"username\": \"jeremyclark\",\n    \"name\": \"Michael Rodriguez\",\n    \"address\": \"340 Williams Club\\nNorth Matthewmouth, NH 89219\",\n    \"birthdate\": \"1979-07-02T04:41:05\",\n    \"email\": \"brittanyhorton@hotmail.com\",\n    \"accounts\": [\n      60664\n    ]\n  },\n  {\n    \"username\": \"wmanning\",\n    \"name\": \"John Barajas\",\n    \"address\": \"39314 Rocha Falls\\nLake Patrickland, KS 54170\",\n    \"birthdate\": \"1972-12-28T02:00:18\",\n    \"email\": \"cheryltrujillo@yahoo.com\",\n    \"accounts\": [\n      304450,\n      892478,\n      465052,\n      999137\n    ]\n  },\n  {\n    \"username\": \"gburton\",\n    \"name\": \"Joseph Price\",\n    \"address\": \"Unit 6261 Box 4483\\nDPO AE 04179\",\n    \"birthdate\": \"1996-08-12T11:56:44\",\n    \"email\": \"eyoung@yahoo.com\",\n    \"accounts\": [\n      514049,\n      468638,\n      587875,\n      409753,\n      569443,\n      612105\n    ]\n  },\n  {\n    \"username\": \"mwells\",\n    \"name\": \"Richard Benson\",\n    \"address\": \"666 Jennifer Shores\\nVincentburgh, CO 13506\",\n    \"birthdate\": \"1976-04-11T02:15:11\",\n    \"email\": \"justinweaver@gmail.com\",\n    \"accounts\": [\n      371349,\n      849780,\n      667881,\n      918539,\n      147085\n    ]\n  },\n  {\n    \"username\": \"hernandezlauren\",\n    \"name\": \"Sandra Armstrong\",\n    \"address\": \"PSC 4729, Box 9374\\nAPO AA 32725\",\n    \"birthdate\": \"1995-05-24T13:38:46\",\n    \"email\": \"walshbryan@yahoo.com\",\n    \"accounts\": [\n      184422,\n      950726,\n      879735,\n      713819,\n      950555,\n      289492\n    ]\n  },\n  {\n    \"username\": \"hmyers\",\n    \"name\": \"Dana Clarke\",\n    \"address\": \"50047 Smith Point Suite 162\\nWilkinsstad, PA 04106\",\n    \"birthdate\": \"1969-06-21T02:39:20\",\n    \"email\": \"vcarter@hotmail.com\",\n    \"accounts\": [\n      627629,\n      55958,\n      771641\n    ]\n  },\n  {\n    \"username\": \"ebeasley\",\n    \"name\": \"Anthony Frost\",\n    \"address\": \"926 Delgado Mall\\nMackenziemouth, MO 07840\",\n    \"birthdate\": \"1978-11-10T19:11:45\",\n    \"email\": \"mary98@hotmail.com\",\n    \"accounts\": [\n      707812,\n      317282\n    ]\n  },\n  {\n    \"username\": \"wendy61\",\n    \"name\": \"James Jones\",\n    \"address\": \"63744 Sanchez Rapids Apt. 483\\nPort Robert, VA 53223\",\n    \"birthdate\": \"1972-04-30T22:01:48\",\n    \"email\": \"gonzalezbethany@hotmail.com\",\n    \"accounts\": [\n      491860,\n      463155\n    ]\n  },\n  {\n    \"username\": \"jeremiah94\",\n    \"name\": \"Tanya Bryant\",\n    \"address\": \"6459 Garcia Parkways\\nNorth Nicholasside, ID 24884\",\n    \"birthdate\": \"1976-12-09T04:31:45\",\n    \"email\": \"linjeremy@gmail.com\",\n    \"accounts\": [\n      234369,\n      437245,\n      333684,\n      120917,\n      248398,\n      909802\n    ]\n  },\n  {\n    \"username\": \"williamstone\",\n    \"name\": \"George Davis\",\n    \"address\": \"389 Newton Corners Suite 668\\nWest Edward, WI 58434\",\n    \"birthdate\": \"1974-06-01T11:40:19\",\n    \"email\": \"jennifer12@gmail.com\",\n    \"accounts\": [\n      703331\n    ]\n  },\n  {\n    \"username\": \"ncardenas\",\n    \"name\": \"David Chung\",\n    \"address\": \"84522 Raymond Stravenue\\nEast Joshuahaven, OR 19575\",\n    \"birthdate\": \"1974-08-12T02:44:16\",\n    \"email\": \"isweeney@hotmail.com\",\n    \"accounts\": [\n      55104,\n      745028,\n      677943,\n      558048,\n      622628\n    ]\n  },\n  {\n    \"username\": \"tknight\",\n    \"name\": \"Seth Gonzalez\",\n    \"address\": \"4975 Davila Wall Apt. 503\\nPort Christophershire, MO 37761\",\n    \"birthdate\": \"1970-03-26T07:35:30\",\n    \"email\": \"paul16@hotmail.com\",\n    \"accounts\": [\n      501408\n    ]\n  },\n  {\n    \"username\": \"avega\",\n    \"name\": \"Brianna Turner\",\n    \"address\": \"02811 Brown Wells\\nNorth Melissaborough, RI 60240\",\n    \"birthdate\": \"1974-12-22T05:56:29\",\n    \"email\": \"kaylaperez@hotmail.com\",\n    \"accounts\": [\n      841135,\n      57322\n    ]\n  },\n  {\n    \"username\": \"carolynmorris\",\n    \"name\": \"Adam Miller\",\n    \"address\": \"89437 Nathan Ford\\nKatietown, LA 03688\",\n    \"birthdate\": \"1990-10-31T20:59:25\",\n    \"email\": \"richard78@gmail.com\",\n    \"accounts\": [\n      523409\n    ]\n  },\n  {\n    \"username\": \"eric10\",\n    \"name\": \"Robert Burns\",\n    \"address\": \"86176 Katherine Common\\nWebbhaven, WA 51980\",\n    \"birthdate\": \"1990-07-17T13:47:12\",\n    \"email\": \"barbaraduncan@gmail.com\",\n    \"accounts\": [\n      205563,\n      616602,\n      387877,\n      460069,\n      442724\n    ]\n  },\n  {\n    \"username\": \"elizabethjackson\",\n    \"name\": \"Matthew Chapman\",\n    \"address\": \"04133 Sandra Park\\nLake Jessicafurt, FL 97317\",\n    \"birthdate\": \"1979-08-29T00:37:07\",\n    \"email\": \"twatkins@yahoo.com\",\n    \"accounts\": [\n      82008,\n      855373,\n      155475,\n      262642,\n      105134\n    ]\n  },\n  {\n    \"username\": \"zcole\",\n    \"name\": \"Shawn Austin\",\n    \"address\": \"84228 Alison Rest Suite 507\\nTimothyshire, NC 75240\",\n    \"birthdate\": \"1970-11-30T15:30:09\",\n    \"email\": \"cameron37@hotmail.com\",\n    \"accounts\": [\n      693557,\n      73934,\n      627788,\n      539248,\n      390126,\n      533671\n    ]\n  },\n  {\n    \"username\": \"candace06\",\n    \"name\": \"Karen Jones\",\n    \"address\": \"41013 Bell Forges\\nPort Josephchester, OR 77912\",\n    \"birthdate\": \"1996-01-19T10:26:09\",\n    \"email\": \"katherinerodgers@hotmail.com\",\n    \"accounts\": [\n      920666\n    ]\n  },\n  {\n    \"username\": \"melissaho\",\n    \"name\": \"Ashley Jackson\",\n    \"address\": \"01132 Gordon Bypass Apt. 638\\nHeatherfort, ID 72393\",\n    \"birthdate\": \"1971-07-15T15:57:46\",\n    \"email\": \"tmccoy@hotmail.com\",\n    \"accounts\": [\n      405559,\n      564812,\n      447601,\n      682382,\n      446474\n    ]\n  },\n  {\n    \"username\": \"jennifer33\",\n    \"name\": \"Rebecca Smith\",\n    \"address\": \"363 Randall Path Suite 435\\nSouth Alexanderfurt, ME 62392\",\n    \"birthdate\": \"1991-11-14T05:45:14\",\n    \"email\": \"kimberlyhunter@yahoo.com\",\n    \"accounts\": [\n      212219,\n      954953,\n      558864,\n      459245\n    ]\n  },\n  {\n    \"username\": \"hthornton\",\n    \"name\": \"Jacob Green\",\n    \"address\": \"7452 Lopez Plain Suite 634\\nEast Samanthamouth, IN 86521\",\n    \"birthdate\": \"1992-01-06T10:06:50\",\n    \"email\": \"gjohnson@gmail.com\",\n    \"accounts\": [\n      691668,\n      340147,\n      154636\n    ]\n  },\n  {\n    \"username\": \"hurstmatthew\",\n    \"name\": \"Stacey Grimes\",\n    \"address\": \"0959 Sean Manor\\nGregoryville, IL 51370\",\n    \"birthdate\": \"1970-11-14T00:00:19\",\n    \"email\": \"calderonchad@hotmail.com\",\n    \"accounts\": [\n      990274,\n      300879,\n      280906,\n"
