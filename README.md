CSCI class project - representing c++ code in memory before and after compiling to Assembly

## Demo
https://mem-track-6c05e.firebaseapp.com/

## Running

### Start the backend server (requires python 3)

`cd backend`

`virtualenv env`

`source env/bin/activate`

`pip install -r requirements.txt`

`python main.py`

### Start the frontend server (requires yarn/node)

Set the backend server endpoint in `frontend\src\app.js` (line 3) to "http://localhost:5000" for development or "https://mem-track-6c05e.appspot.com" for production

`cd frontend`

`yarn install`

`yarn start`
