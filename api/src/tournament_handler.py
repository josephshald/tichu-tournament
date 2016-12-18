import webapp2
import json

from google.appengine.api import users
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import TourneyDoesNotExistStatus
from handler_utils import SetErrorStatus
from models import Tournament

class TourneyHandler(webapp2.RequestHandler):
  ''' Handles reuqests to /api/tournament/:id. Responsible all things related
      to any one specific tournament.
  '''

  def get(self, id):
    ''' Returns tournament metadata for tournament with id.

        Args: 
          id: tournament ID to look up. Tournament must already have been
              created.
    ''' 
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    if not is_int(id):
      TourneyDoesNotExistStatus(self.response, id)
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    
    if (not tourney.metadata) or (not tourney.owner_id):
      SetErrorStatus(self.response, 500, "Invalid tournament data",
                     "Tournament data is corrupted. Consider starting a " + 
                         "new one.")
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(),
                                                       tourney, id):
      return

    combined_dict = json.loads(tourney.metadata)
    combined_dict["hands"] = json.loads(tourney.hands) if tourney.hands else []
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps(combined_dict, indent=2))


  def put(self, id):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return
      
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(),
                                                       tourney, id):
      return

    request_dict = self._ParseRequestInfoAndMaybeSetStatus()
    if not request_dict:
      return

    name = request_dict["name"]
    no_pairs = request_dict['no_pairs']
    no_boards = request_dict['no_boards']
    player_list = request_dict.get('players')
    if not self._CheckValidTournamentInfoAndMaybeSetStatus(name, no_pairs,
                                                           no_boards,
                                                           player_list):
      return

    self.response.set_status(204)
    # Need to update documentation, this leaves available hand scores alone.
    metadata_dict = {"name": name, "no_pairs": no_pairs,
                     "no_boards": no_boards}
    if player_list:
      metadata_dict["players"] = player_list
    tourney.metadata = json.dumps(metadata_dict)
    tourney.put()  


  def delete(self, id):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(),
                                                       tourney, id):
      return

    self.response.set_status(204)
    tourney.key.delete()  


  def _ParseRequestInfoAndMaybeSetStatus(self):
    ''' Parses the body of the request. Checks if the body is valid JSON with
        all the proper fields set. Checks if the number of boards and number of 
        pairs are valid numbers. If not sets the response with the appropriate
        status and error message.
    '''
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    if not isinstance(request_dict.get('no_pairs'), int):
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "no_pairs must be an integer")
      return None
    elif not isinstance(request_dict.get('no_boards'), int):
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "no_boards must be an integer")
      return None
    elif request_dict.get('players'):
      player_list = request_dict.get('players')
      for player in player_list:
        if not player['pair_no']:
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Player must have corresponding pair number if present.")
          return None
        if not isinstance(player['pair_no'], int):
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Player pair number must be an integer, was {}".format(
                             player['pair_no']))
          return None
    return request_dict


  def _CheckValidTournamentInfoAndMaybeSetStatus(self, name, no_pairs,
                                                 no_boards, players=None):
    ''' Checks if the input is valid and sane. 
        If not sets the response with the appropriate status and error message.
        Assumes no_pairs and no_boards are integers.
    '''
    if not name or name == "":
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Tournament name must be nonempty")
      return False
    elif no_pairs < 2:
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Number of pairs must be > 1, was {}".format(no_pairs))
      return False
    elif no_boards < 1:
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Number of boards must be > 0, was {}".format(no_boards))
      return False
    elif players:
      for player in players:
        if player['pair_no'] < 1 or player['pair_no'] > no_pairs:
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Player pair must be between 1 and no_pairs, was {}.".format(
                             player['pair_no']))
          return False
    return True