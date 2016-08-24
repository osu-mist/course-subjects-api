package edu.oregonstate.mist.coursesubjectsapi.resources

import com.codahale.metrics.annotation.Timed
import edu.oregonstate.mist.api.Resource
import edu.oregonstate.mist.api.AuthenticatedUser
import edu.oregonstate.mist.api.jsonapi.ResultObject
import edu.oregonstate.mist.coursesubjectsapi.dao.SubjectsDAO
import io.dropwizard.auth.Auth
import org.slf4j.Logger
import org.slf4j.LoggerFactory

import javax.ws.rs.GET
import javax.ws.rs.Path
import javax.ws.rs.Produces
import javax.ws.rs.core.Response
import javax.ws.rs.core.MediaType

@Path('/subjects/')
class SubjectResource extends Resource {
    Logger logger = LoggerFactory.getLogger(SubjectResource.class)

    private SubjectsDAO subjectsDAO

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    @Timed
    public Response classSearch(@Auth AuthenticatedUser _) {
        try {
            def response = subjectsDAO.getData()
            ResultObject resultObject = new ResultObject(data: response.data)

            ok(resultObject).build()
        } catch (Exception e) {
            logger.error("Exception while getting course subjects", e)
            internalServerError("Woot you found a bug for us to fix!").build()
        }
    }
}