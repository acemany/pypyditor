package textAreaComponent.textAreaEvents;

import java.awt.*;

public class TextChangeEvent {
    private String text;
    private Component component;

    public TextChangeEvent(Component component, String text) {
        this.component = component;
        this.text = text;
    }

    public Component getComponent() {
        return component;
    }

    public String getText() {
        return text;
    }
}
