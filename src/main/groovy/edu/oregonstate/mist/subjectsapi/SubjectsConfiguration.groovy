package edu.oregonstate.mist.subjectsapi

import com.fasterxml.jackson.annotation.JsonProperty
import edu.oregonstate.mist.api.Configuration
import io.dropwizard.client.HttpClientConfiguration

import javax.validation.Valid
import javax.validation.constraints.NotNull

class SubjectsConfiguration extends Configuration {
    @JsonProperty('subjects')
    @NotNull
    @Valid
    Map<String, String> classSearch

    @Valid
    @NotNull
    private HttpClientConfiguration httpClient = new HttpClientConfiguration()

    @JsonProperty("httpClient")
    public HttpClientConfiguration getHttpClientConfiguration() {
        httpClient
    }

    @JsonProperty("httpClient")
    public void setHttpClientConfiguration(HttpClientConfiguration httpClient) {
        this.httpClient = httpClient
    }
}
