"use strict";
(function(angular) {
  /**
   * Service to maintain a cache of tournament-related model objects.
   *
   * @constructor
   * @name TichuTournamentStore
   * @param {angular.$cacheFactory} $cacheFactory
   * @ngInject
   */
  function TichuTournamentStore($cacheFactory) {
    /**
     * The cache of TournamentHeader instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentHeaderCache = $cacheFactory("TournamentHeaders");

    /**
     * The cache of TournamentPair instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentPairCache = $cacheFactory("TournamentPairs");

    /**
     * The cache of Tournament instances.
     *
     * @type {angular.$cacheFactory.Cache}
     * @private
     */
    this._tournamentCache = $cacheFactory("Tournaments");
  }

  /**
   * Retrieves or creates a header in the cache, and updates its fields if requested.
   * @param {string} id The ID of the tournament header to retrieve or create.
   * @returns {tichu.TournamentHeader}
   */
  TichuTournamentStore.prototype.getOrCreateTournamentHeader = function getOrCreateTournamentHeader(id) {
    var header = this._tournamentHeaderCache.get(id);
    if (!header) {
      header = new tichu.TournamentHeader(id);
      this._tournamentHeaderCache.put(id, header);
    }
    return header;
  };

  /**
   * Retrieves or creates a cached pair for the given tournament.
   * @param {string} id The tournament ID to look for pairs from.
   * @param {number} pairNo The 1-indexed number of the pair to retrieve.
   * @returns {tichu.TournamentPair}
   */
  TichuTournamentStore.prototype.getOrCreateTournamentPair = function getOrCreateTournamentPair(id, pairNo) {
    var cacheKey = encodeURIComponent(id) + "/" + encodeURIComponent(pairNo.toString());
    var pair = this._tournamentPairCache.get(cacheKey);
    if (!pair) {
      pair = new tichu.TournamentPair(pairNo);
      this._tournamentPairCache.put(cacheKey, pair);
    }
    return pair;
  };

  /**
   * Returns whether the tournament exists in the cache or not without creating it.
   * @param {string} id The ID of the tournament to retrieve or create.
   * @returns {boolean}
   */
  TichuTournamentStore.prototype.hasTournament = function hasTournament(id) {
    return !!this._tournamentCache.get(id);
  };

  /**
   * Retrieves or creates a tournament in the cache, and updates its fields if requested.
   * @param {string} id The ID of the tournament to retrieve or create.
   * @returns {tichu.Tournament}
   */
  TichuTournamentStore.prototype.getOrCreateTournament = function getOrCreateTournament(id) {
    var tournament = this._tournamentCache.get(id);
    if (!tournament) {
      tournament = new tichu.Tournament(this.getOrCreateTournamentHeader(id));
      this._tournamentCache.put(id, tournament);
    }
    return tournament;
  };

  angular.module("tichu-tournament-store", ["ng"])
      .service("TichuTournamentStore", TichuTournamentStore);
})(angular);