package core;

import java.util.Properties;

// This class is created to be able to modify settings per host in the self-studier movement model because there will only be one group of self-studiers but each host will have different route files.

public class ModifiableSettings extends Settings {
    public Properties modifications;

	public ModifiableSettings(String namespace) {
		super(namespace);
		this.modifications = new Properties();
	}

	public ModifiableSettings(Settings proto) {
		super(proto.getNameSpace());
		this.modifications = new Properties();

		if (proto.getSecondaryNameSpace() != null) {
			this.setSecondaryNamespace(proto.getSecondaryNameSpace());
		}

		if (proto instanceof ModifiableSettings) {
			ModifiableSettings modifiableProto = (ModifiableSettings) proto;
			this.modifications.putAll(modifiableProto.modifications);
		}
	}

	// Needed to be able to set route file setting

	public void setSetting(String key, String value) {
		this.modifications.setProperty(key, value);
	}

	@Override
	public String getSetting(String key) {
		if (this.modifications.containsKey(key)) {
			return this.modifications.getProperty(key);
		}
		return super.getSetting(key);
	}
	
}