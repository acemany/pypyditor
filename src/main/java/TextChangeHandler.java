import com.google.common.eventbus.Subscribe;
import textAreaComponent.textAreaEvents.TextChangeEvent;

public class TextChangeHandler {
    @Subscribe
    public void handleTextChangeEvent(TextChangeEvent e) {
        System.out.println(e.getComponent());
        System.out.println(e.getText());
    }
}
