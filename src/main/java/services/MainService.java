package services;

import com.google.common.eventbus.EventBus;
import groovy.lang.Singleton;


@Singleton
public class MainService {
    public static MainService INSTANCE = new MainService();
    public EventBus eventBus;

    private MainService() {
        eventBus  = new EventBus();
    }
}
