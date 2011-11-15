package org.mozilla.android.sync.repositories;

import org.mozilla.android.sync.repositories.domain.Record;

public abstract class RepositorySession {

  Repository repository;
  SyncCallbackReceiver callbackReceiver;
  // TODO logger and logger level here

  public RepositorySession(Repository repository, SyncCallbackReceiver callbackReceiver) {
    this.repository = repository;
    this.callbackReceiver = callbackReceiver;
  }

  public abstract void guidsSince(long timestamp, RepositoryCallbackReceiver receiver);
  public abstract void fetchSince(long timestamp, RepositoryCallbackReceiver receiver);
  public abstract void fetch(String[] guids, RepositoryCallbackReceiver receiver);

  // Test function only
  public abstract void fetchAll(RepositoryCallbackReceiver receiver);

  public abstract void store(Record record, RepositoryCallbackReceiver receiver);
  public abstract void wipe(RepositoryCallbackReceiver receiver);
  public abstract void begin(RepositoryCallbackReceiver receiver);
  public abstract void finish(RepositoryCallbackReceiver receiver);

}
